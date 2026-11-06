#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CỔNG G0 — Kiểm tra môi trường trước khi tải bất cứ thứ gì.

Chạy:
    python tools/du_lieu/kiem_tra_moi_truong.py
    python tools/du_lieu/kiem_tra_moi_truong.py --thu-muc data --can-trong 12

Mã thoát: 0 = đủ điều kiện · 1 = có lỗi chặn (không được chạy bước sau).
"""
from __future__ import annotations

# ── Windows: console mặc định cp1252 → in tiếng Việt/emoji sẽ văng UnicodeEncodeError ──
import sys as _sys
for _luong in (_sys.stdout, _sys.stderr):
    try:
        _luong.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


import argparse
import json
import platform
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# ── bảng kết quả ───────────────────────────────────────────────────────
DONG: list[tuple[str, str, str]] = []   # (mức, tên, ghi chú)  mức: OK / CẢNH BÁO / CHẶN


def ghi(muc: str, ten: str, ghi_chu: str = "") -> None:
    DONG.append((muc, ten, ghi_chu))


def kiem_python() -> None:
    v = sys.version_info
    if v >= (3, 10):
        ghi("OK", "Python", f"{v.major}.{v.minor}.{v.micro}")
    else:
        ghi("CHẶN", "Python", f"{v.major}.{v.minor} — cần ≥ 3.10")


def kiem_lenh(ten: str, bat_buoc: bool) -> None:
    duong = shutil.which(ten)
    if duong:
        try:
            r = subprocess.run([ten, "--version"], capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=20)
            phien_ban = (r.stdout or r.stderr).strip().splitlines()[0][:60]
        except Exception:
            phien_ban = duong
        ghi("OK", ten, phien_ban)
    else:
        ghi("CHẶN" if bat_buoc else "CẢNH BÁO", ten, "không tìm thấy trong PATH")


def kiem_goi(ten: str, bat_buoc: bool, vi_sao: str) -> None:
    try:
        m = __import__(ten)
        ghi("OK", f"gói {ten}", getattr(m, "__version__", "?") + f" — {vi_sao}")
    except Exception:
        ghi("CHẶN" if bat_buoc else "CẢNH BÁO", f"gói {ten}",
            f"thiếu — cài: pip install {ten}  ({vi_sao})")


def kiem_dia(thu_muc: Path, can_gb: float) -> None:
    thu_muc.mkdir(parents=True, exist_ok=True)
    dung = shutil.disk_usage(str(thu_muc))
    trong_gb = dung.free / 1024 ** 3
    if trong_gb >= can_gb:
        ghi("OK", "Dung lượng trống", f"{trong_gb:.1f} GB (cần {can_gb:.0f} GB)")
    else:
        ghi("CHẶN", "Dung lượng trống", f"{trong_gb:.1f} GB < {can_gb:.0f} GB cần thiết")


def main() -> int:
    ap = argparse.ArgumentParser(description="Kiểm tra môi trường cho Pha A (dữ liệu)")
    ap.add_argument("--thu-muc", default="data", help="thư mục dữ liệu (mặc định: data)")
    ap.add_argument("--can-trong", type=float, default=12.0,
                    help="số GB trống tối thiểu (mặc định 12 = T0+T1)")
    ap.add_argument("--json", default="", help="ghi kết quả ra tệp JSON")
    a = ap.parse_args()

    goc = Path(__file__).resolve().parents[2]
    thu_muc = (goc / a.thu_muc) if not Path(a.thu_muc).is_absolute() else Path(a.thu_muc)

    ghi("OK", "Hệ điều hành", f"{platform.system()} {platform.release()} · {platform.machine()}")
    ghi("OK", "Thư mục gốc dự án", str(goc))

    kiem_python()
    kiem_lenh("git", bat_buoc=True)
    kiem_lenh("ffmpeg", bat_buoc=False)
    kiem_goi("numpy", True, "xử lý tín hiệu")
    kiem_goi("pandas", True, "manifest")
    kiem_goi("soundfile", True, "đọc/ghi WAV")
    kiem_goi("huggingface_hub", False, "tải bộ dữ liệu từ Hugging Face")
    kiem_goi("datasets", False, "chỉ cần nếu dùng chế độ streaming")
    kiem_dia(thu_muc, a.can_trong)

    rong = max(len(t) for _, t, _ in DONG)
    print("=" * (rong + 60))
    print("  CỔNG G0 — KIỂM TRA MÔI TRƯỜNG")
    print("=" * (rong + 60))
    for muc, ten, gc in DONG:
        print(f"  {muc:<9} {ten:<{rong}}  {gc}")
    so_chan = sum(1 for m, _, _ in DONG if m == "CHẶN")
    so_canh_bao = sum(1 for m, _, _ in DONG if m == "CẢNH BÁO")
    print("-" * (rong + 60))
    print(f"  CHẶN: {so_chan} · CẢNH BÁO: {so_canh_bao} · TỔNG: {len(DONG)}")
    print("=" * (rong + 60))

    if so_chan:
        print("\n  ❌ CHƯA ĐẠT G0 — sửa các mục CHẶN rồi chạy lại. Không được tải dữ liệu.")
    else:
        print("\n  ✅ ĐẠT G0 — được chuyển sang bước A1.3 (tải dữ liệu).")

    if a.json:
        ra = Path(a.json)
        ra.parent.mkdir(parents=True, exist_ok=True)
        ra.write_text(json.dumps({
            "thoi_diem": datetime.now().isoformat(timespec="seconds"),
            "may": f"{platform.system()} {platform.release()}",
            "thu_muc": str(thu_muc),
            "so_chan": so_chan,
            "so_canh_bao": so_canh_bao,
            "dong": [{"muc": m, "ten": t, "ghi_chu": g} for m, t, g in DONG],
        }, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"  Đã ghi: {ra}")

    return 1 if so_chan else 0


if __name__ == "__main__":
    raise SystemExit(main())
