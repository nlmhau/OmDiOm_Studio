#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
G-TT — Tạo / kiểm vân tay SHA256 cho một thư mục. Chạy được trên Windows, macOS, Linux.

    python tools/du_lieu/tao_van_tay.py --tao  data/SACH/v1
    python tools/du_lieu/tao_van_tay.py --kiem data/SACH/v1
    python tools/du_lieu/tao_van_tay.py --kiem data/SACH/v1 --json data/LOG/van_tay.json

Thay cho chuỗi lệnh chỉ chạy trên Linux:
    find wav -name "*.wav" -print0 | sort -z | xargs -0 sha256sum > SHA256SUMS
    sha256sum -c SHA256SUMS

Định dạng tệp giống `sha256sum` chuẩn (hash + 2 dấu cách + đường dẫn tương đối), nên công cụ
Linux vẫn đọc được.
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
import hashlib
import json
from datetime import datetime
from pathlib import Path

GOC = Path(__file__).resolve().parents[2]
DUOI_MAC_DINH = {".wav", ".flac", ".mp3", ".pt", ".csv", ".json"}
BO_QUA = {"__pycache__", ".git", ".cache", ".venv"}


def _bam(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for khoi in iter(lambda: f.read(1 << 20), b""):
            h.update(khoi)
    return h.hexdigest()


def liet_ke(goc: Path, duoi: set[str]) -> list[Path]:
    ra = []
    for p in sorted(goc.rglob("*")):
        if not p.is_file() or p.suffix.lower() not in duoi:
            continue
        if any(x in BO_QUA for x in p.parts):
            continue
        if p.name in ("SHA256SUMS",):
            continue
        ra.append(p)
    return sorted(ra, key=lambda x: x.relative_to(goc).as_posix())


def tao(goc: Path, duoi: set[str]) -> int:
    ds = liet_ke(goc, duoi)
    if not ds:
        print(f"❌ Không có tệp nào loại {sorted(duoi)} trong {goc}")
        return 1
    dong = [f"{_bam(p)}  {p.relative_to(goc).as_posix()}" for p in ds]
    ra = goc / "SHA256SUMS"
    ra.write_text("\n".join(dong) + "\n", encoding="utf-8")
    print(f"✅ {len(ds)} tệp → {ra}")
    print(f"   Tổng dung lượng: {sum(p.stat().st_size for p in ds) / 1024 ** 2:.2f} MB")
    return 0


def kiem(goc: Path, json_ra: str = "") -> int:
    ra = goc / "SHA256SUMS"
    if not ra.exists():
        print(f"❌ Không thấy {ra} — chạy --tao trước.")
        return 1
    dung, sai, mat = 0, [], []
    for dong in ra.read_text(encoding="utf-8").splitlines():
        dong = dong.strip()
        if not dong or len(dong) < 66:
            continue
        ha, duong = dong[:64], dong[66:].strip()
        p = goc / duong
        if not p.exists():
            mat.append(duong)
            continue
        if _bam(p) == ha:
            dung += 1
        else:
            sai.append(duong)
    tong = dung + len(sai) + len(mat)
    print("-" * 70)
    print(f"  Khớp: {dung}/{tong} · lệch: {len(sai)} · thiếu tệp: {len(mat)}")
    for d in sai[:10]:
        print(f"    ✗ lệch nội dung: {d}")
    for d in mat[:10]:
        print(f"    ✗ thiếu tệp: {d}")
    print("-" * 70)
    if not sai and not mat:
        print("  ✅ VÂN TAY KHỚP — dữ liệu không bị sửa từ lúc tạo")
        rc = 0
    else:
        print("  ❌ KHÔNG KHỚP — có tệp bị sửa hoặc bị xoá. Không được gọi là đã chốt.")
        rc = 1
    if json_ra:
        j = Path(json_ra)
        if not j.is_absolute():
            j = GOC / j
        j.parent.mkdir(parents=True, exist_ok=True)
        j.write_text(json.dumps({
            "thu_muc": str(goc), "thoi_diem": datetime.now().isoformat(timespec="seconds"),
            "tong": tong, "khop": dung, "lech": sai, "thieu": mat,
        }, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"  Đã ghi: {j}")
    return rc


def main() -> int:
    ap = argparse.ArgumentParser(description="Tạo/kiểm vân tay SHA256 (đa nền tảng)")
    ap.add_argument("--tao", default="", help="thư mục cần tạo SHA256SUMS")
    ap.add_argument("--kiem", default="", help="thư mục cần kiểm")
    ap.add_argument("--duoi", default="", help="đuôi tệp, cách nhau dấu phẩy (mặc định wav,flac,mp3,pt,csv,json)")
    ap.add_argument("--json", default="", help="ghi kết quả kiểm ra JSON")
    a = ap.parse_args()
    duoi = ({f".{x.strip().lstrip('.')}" for x in a.duoi.split(",") if x.strip()}
            or DUOI_MAC_DINH)

    if not a.tao and not a.kiem:
        ap.print_help()
        return 1
    if a.tao:
        goc = Path(a.tao)
        return tao(goc if goc.is_absolute() else GOC / goc, duoi)
    goc = Path(a.kiem)
    return kiem(goc if goc.is_absolute() else GOC / goc, a.json)


if __name__ == "__main__":
    raise SystemExit(main())
