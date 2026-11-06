#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A1.7 — Cắt clip tham chiếu 3 / 6 / 10 giây cho mỗi giọng (đóng giả định G1).

    python tools/du_lieu/tao_ref.py --kiem          # xem việc sẽ làm
    python tools/du_lieu/tao_ref.py \
        --tep ghi_am/u_linh.wav --van-ban "Chị Hằng ở phố cổ vẫn nhớ buổi chiều đọc sách." \
        --nguoi-noi U_LINH --gioi-tinh nu --vung-mien nam --dong-y \
        --ngay-thu 2026-10-26 --thiet-bi "tai nghe kèm mic"

Nguyên tắc đạo đức: KHÔNG tạo clip nếu thiếu --dong-y (người đọc đồng ý cho dùng
giọng của mình trong đồ án). Cờ này là bắt buộc, không có mặc định.
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
import sys
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd
import soundfile as sf

GOC = Path(__file__).resolve().parents[2]
REF = GOC / "data" / "REF"
MANIFEST = REF / "ref_manifest.csv"
DO_DAI = (3.0, 6.0, 10.0)


def cat_tieng(y: np.ndarray, sr: int) -> np.ndarray:
    """Bỏ im lặng đầu (giữ 0,1 s đệm) để clip bắt đầu đúng chỗ có tiếng."""
    khung, buoc = int(0.02 * sr), int(0.01 * sr)
    if len(y) < khung * 2:
        return y
    n = 1 + (len(y) - khung) // buoc
    rms = np.array([float(np.sqrt(np.mean(y[i * buoc: i * buoc + khung] ** 2) + 1e-12))
                    for i in range(n)])
    nguong = max(float(rms.max()) * 0.03, 1e-4)
    co = np.where(rms > nguong)[0]
    if not len(co):
        return y
    dau = max(0, int(co[0]) * buoc - int(0.10 * sr))
    cuoi = min(len(y), (int(co[-1]) + 1) * buoc + khung + int(0.15 * sr))
    return y[dau:cuoi]


def main() -> int:
    ap = argparse.ArgumentParser(description="Cắt clip tham chiếu 3/6/10 giây")
    ap.add_argument("--tep", required=True, help="bản ghi dài (≥10 giây có tiếng)")
    ap.add_argument("--van-ban", required=True, help="đúng câu người đọc đã đọc")
    ap.add_argument("--nguoi-noi", required=True, help="mã giọng, ví dụ U_LINH")
    ap.add_argument("--gioi-tinh", default="khong_ro", choices=["nam", "nu", "khong_ro"])
    ap.add_argument("--vung-mien", default="khong_ro", choices=["bac", "trung", "nam", "khong_ro"])
    ap.add_argument("--ngay-thu", default=date.today().isoformat())
    ap.add_argument("--thiet-bi", default="khong_ro")
    ap.add_argument("--dong-y", action="store_true", help="BẮT BUỘC: người đọc đã đồng ý")
    ap.add_argument("--kiem", action="store_true", help="chỉ kiểm tệp, không cắt")
    a = ap.parse_args()

    if not a.dong_y:
        print("❌ Thiếu --dong-y. Không tạo clip tham chiếu khi chưa có đồng ý của người đọc.")
        print("   Đây là quy tắc đạo đức của dự án, không phải tuỳ chọn.")
        return 2

    p = Path(a.tep) if Path(a.tep).is_absolute() else GOC / a.tep
    if not p.exists():
        print(f"❌ Không thấy tệp: {p}")
        return 1
    y, sr = sf.read(str(p), dtype="float32", always_2d=False)
    if getattr(y, "ndim", 1) > 1:
        y = y.mean(axis=1)
    y = cat_tieng(np.asarray(y, dtype=np.float32), sr)
    dai = len(y) / sr
    print(f"Tệp: {p.name} · {sr} Hz · sau khi cắt im lặng: {dai:.2f} giây")
    if dai < 10.0:
        print(f"❌ Chỉ còn {dai:.2f} giây — cần ≥ 10 giây để cắt đủ 3 cỡ clip.")
        return 1
    if a.kiem:
        print(f"Đủ điều kiện. Sẽ tạo {len(DO_DAI)} clip: "
              + ", ".join(f"{d:g}s" for d in DO_DAI))
        return 0

    dong = []
    for d in DO_DAI:
        n = int(d * sr)
        clip = y[:n]
        ten = f"{a.nguoi_noi}_{int(d):02d}s.wav"
        dich = REF / "wav" / ten
        dich.parent.mkdir(parents=True, exist_ok=True)
        sf.write(str(dich), clip, sr, subtype="PCM_16")
        dong.append({
            "clip_id": f"{a.nguoi_noi}_{int(d):02d}s",
            "nguoi_noi": a.nguoi_noi,
            "gioi_tinh": a.gioi_tinh,
            "vung_mien": a.vung_mien,
            "thoi_luong_giay": round(len(clip) / sr, 3),
            "tan_so_mau": sr,
            "van_ban": a.van_ban,
            "duong_dan": str(dich.relative_to(GOC)),
            "sha256": hashlib.sha256(dich.read_bytes()).hexdigest(),
            "ngay_thu": a.ngay_thu,
            "thiet_bi": a.thiet_bi,
            "dong_y": "co",
            "nguon_goc": str(p.relative_to(GOC)) if p.is_relative_to(GOC) else str(p),
        })
        print(f"  ✓ {dich.relative_to(GOC)}  ({len(clip) / sr:.2f}s)")

    REF.mkdir(parents=True, exist_ok=True)
    df_moi = pd.DataFrame(dong)
    if MANIFEST.exists():
        df_cu = pd.read_csv(MANIFEST, encoding="utf-8-sig")
        df_cu = df_cu[~df_cu["clip_id"].isin(df_moi["clip_id"])]
        df_moi = pd.concat([df_cu, df_moi], ignore_index=True)
    df_moi.to_csv(MANIFEST, index=False, encoding="utf-8-sig")
    (REF / f"{a.nguoi_noi}_thong_tin.json").write_text(json.dumps({
        "nguoi_noi": a.nguoi_noi, "gioi_tinh": a.gioi_tinh, "vung_mien": a.vung_mien,
        "ngay_thu": a.ngay_thu, "thiet_bi": a.thiet_bi,
        "dong_y": "Người đọc đồng ý dùng giọng cho đồ án học thuật (ghi ngày "
                  f"{a.ngay_thu}); không dùng cho mục đích giả mạo.",
        "cau_doc": a.van_ban,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"→ {MANIFEST.relative_to(GOC)}  ({len(df_moi)} dòng)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
