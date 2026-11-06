#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A1.2 — Dựng cây thư mục data/ đúng hợp đồng, kèm tệp chỉ dẫn tại từng chỗ.

    python tools/du_lieu/tao_cay_thu_muc.py
    python tools/du_lieu/tao_cay_thu_muc.py --kiem     # chỉ xem, không tạo

Không ghi đè gì đã có. Chạy bao nhiêu lần cũng an toàn.
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
from pathlib import Path

GOC = Path(__file__).resolve().parents[2]
D = GOC / "data"

# (đường dẫn, tệp chỉ dẫn đặt trong đó, nội dung)
CAY = [
    ("RAW", "README.md", """# data/RAW — DỮ LIỆU THÔ, CHỈ ĐỌC

Không sửa, không xoá, không ghi đè tệp trong thư mục này.
Sai thì tạo bộ mới trong `data/SACH/v2`, không sửa bộ cũ.

| Thư mục | Chứa gì |
|---|---|
| `_nguon/<mã>.json` | giấy khai sinh của từng nguồn (URL, phiên bản, giấy phép, số tệp, thời điểm) |
| `_tai_ve/` | tệp nén tải trực tiếp (.tar.gz, .zip) |
| `giong_pt/` | **7 tệp giọng .pt do nhóm tự thu** — xem README trong đó |
| `omnivoice/` | mã nguồn model (git clone) |
| `vivos/` | dữ liệu VIVOS đã bung |
| `_manifest_tho.csv` | đầu vào của `lam_sach.py` |
"""),
    ("RAW/giong_pt", "README.md", """# 7 TỆP GIỌNG THAM CHIẾU (.pt)

**Đặt đúng 7 tệp vào thư mục này, giữ nguyên tên gốc:**

```
u_linh.pt
giong_ong_gia.pt
ke.pt
tran_thy.pt
giong_nu_tre.pt
giong_trai_tre.pt
giong_tre_em.pt
```

Không đổi tên, không đổi đuôi: notebook v5 tìm đúng các tên này (cell 3).
Không mở thư mục con. Không để bản sao `.pt` nào khác — trùng tên sẽ gây nhầm.

## Đây là dữ liệu gì
`VoiceClonePrompt.save()` của OmniVoice — định dạng **chính thức**, chứa mã âm học +
embedding người nói + lời thoại tham chiếu. Dùng trực tiếp để sinh giọng, không chuyển đổi.

## Sau khi đặt tệp, chạy 2 lệnh
```bash
# 1. ghi vân tay (để biết sau này ai sửa tệp)
python tools/du_lieu/tao_cay_thu_muc.py --van-tay

# 2. soi cấu trúc + xem có lấy lại được WAV không
python tools/du_lieu/kiem_pt.py --thu-muc data/RAW/giong_pt
```

## Cần kèm theo
Điền `data/REF/DONG_Y_7_GIONG.md` (mẫu: `docs/PHIEU-DONG-Y-GIONG.md`).
Không có tờ đó thì vẫn chạy được, nhưng báo cáo sẽ thiếu phần truy vết nguồn giọng.
"""),
    ("REF", "README.md", """# data/REF — GIỌNG THAM CHIẾU (đầu ra)

Thư mục này **sinh ra từ** `data/RAW/giong_pt/`, không phải nơi chứa tệp gốc.

| Tệp / thư mục | Nội dung |
|---|---|
| `ref_manifest.csv` | 13 cột: clip_id, mã giọng, cỡ giây, lời thoại, vân tay, đồng ý… |
| `wav/<MÃ>_<03|06|10>s.wav` | clip cắt ra (nếu giải mã được từ .pt) |
| `DONG_Y_7_GIONG.md` | phiếu đồng ý điền bù |
| `<MÃ>_thong_tin.json` | thông tin từng giọng |
"""),
    ("SACH", "README.md", """# data/SACH — BỘ DỮ LIỆU ĐÃ LỌC

Mỗi phiên bản một thư mục: `v1/`, `v2/`… **Không sửa `v1` sau khi đã chốt.**

Tạo bằng: `python tools/du_lieu/lam_sach.py --tho data/RAW/_manifest_tho.csv --ten-bo v1`
Kiểm bằng: `python tools/du_lieu/kiem_du_lieu.py --bo v1`
"""),
    ("LOG", "README.md", """# data/LOG — NHẬT KÝ VÀ BÁO CÁO KIỂM

| Tệp | Nội dung |
|---|---|
| `NHAT_KY.md` | mỗi bước một dòng: thời điểm, lệnh, kết quả, tệp sinh ra |
| `moi_truong.json` | kết quả cổng G0 |
| `kiem_du_lieu.json` | kết quả cổng G2–G8 |
| `kiem_pt.json` | kết quả soi 7 tệp .pt |
| `viet_hoa_can_sua.csv` | các chỗ còn tiếng Anh |
"""),
    ("RAW/_nguon", "README.md", """# data/RAW/_nguon — SỔ NGUỒN

Mỗi nguồn đã tải có **đúng một** tệp `<mã>.json`: URL, phiên bản/commit, giấy phép, số tệp,
dung lượng, thời điểm. Do `tai_du_lieu.py` tự ghi.

Nguồn `giong_pt` (7 giọng nhóm tự thu) cũng phải có mặt ở đây — do
`tao_cay_thu_muc.py --van-tay` tạo.
"""),
]


def tao(kiem: bool) -> int:
    so_tao = so_co = 0
    for duong, ten, noi_dung in CAY:
        thu_muc = D / duong
        if kiem:
            print(f"  {'có ' if thu_muc.exists() else 'THIẾU'}  {thu_muc.relative_to(GOC)}")
            continue
        thu_muc.mkdir(parents=True, exist_ok=True)
        so_tao += 1
        tep = thu_muc / ten
        if not tep.exists():
            tep.write_text(noi_dung, encoding="utf-8")
        else:
            so_co += 1
    if kiem:
        return 0
    # chặn ở gốc repo — đây mới là chỗ git thật sự đọc để bỏ qua cả thư mục
    goc_ignore = GOC / ".gitignore"
    can = ["data/", "*.part", "__pycache__/", ".venv/", "*.pyc", ".cache/"]
    if not goc_ignore.exists():
        goc_ignore.write_text("\n".join(can) + "\n", encoding="utf-8")
        print(f"  tạo {goc_ignore.name}: {', '.join(can)}")
    else:
        hien = goc_ignore.read_text(encoding="utf-8")
        thieu = [c for c in can if c not in hien]
        if thieu:
            goc_ignore.write_text(hien.rstrip() + "\n" + "\n".join(thieu) + "\n", encoding="utf-8")
            print(f"  bổ sung vào .gitignore: {', '.join(thieu)}")
    # chặn thêm một lớp bên trong data/ (phòng khi ai copy thư mục đi nơi khác)
    gitignore = D / ".gitignore"
    if not gitignore.exists():
        gitignore.write_text("*\n!*\n", encoding="utf-8")
    print(f"✅ Đã dựng {so_tao} thư mục ({so_co} tệp chỉ dẫn đã có sẵn, giữ nguyên)")
    return 0


def van_tay(ghi_de: bool = False) -> int:
    """Ghi SHA256SUMS + giấy khai sinh cho 7 tệp .pt."""
    import hashlib
    import json
    from datetime import datetime

    pt_dir = D / "RAW" / "giong_pt"
    ds = sorted(pt_dir.glob("*.pt"))
    if not ds:
        print(f"❌ Chưa có tệp .pt nào trong {pt_dir.relative_to(GOC)}")
        print("   Đặt 7 tệp vào đó rồi chạy lại.")
        return 1

    dong, tong = [], 0
    for p in ds:
        h = hashlib.sha256(p.read_bytes()).hexdigest()
        kb = p.stat().st_size / 1024
        tong += kb
        dong.append(f"{h}  {p.name}")
        print(f"  {p.name:<24} {kb:>9.1f} KB  {h[:16]}…")
    f_sum = pt_dir / "SHA256SUMS"
    if f_sum.exists() and not ghi_de:
        print(f"  ⏭  {f_sum.name} — đã có, giữ nguyên (dùng --ghi-de nếu muốn tạo lại)")
    else:
        f_sum.write_text("\n".join(dong) + "\n", encoding="utf-8")

    nguon = D / "RAW" / "_nguon"
    nguon.mkdir(parents=True, exist_ok=True)
    ban_ghi = {
        "ma_nguon": "giong_pt",
        "ten": "7 giọng tham chiếu do nhóm tự thu (định dạng VoiceClonePrompt)",
        "url": "không có — dữ liệu nội bộ",
        "phien_ban": "omnivoice==0.2.1 (bản ghi tệp .pt)",
        "giay_phep": "Do nhóm sở hữu; có đồng ý của người đọc — xem data/REF/DONG_Y_7_GIONG.md",
        "tang": 0,
        "duong_dan": "data/RAW/giong_pt",
        "so_tep": len(ds),
        "dung_luong_mb": round(tong / 1024, 2),
        "thoi_diem": datetime.now().isoformat(timespec="seconds"),
        "ghi_chu": "Không phát hành lại. Không dùng cho mục đích giả mạo.",
    }
    f_ks = nguon / "giong_pt.json"
    if f_ks.exists() and not ghi_de:
        print(f"  ⏭  {f_ks.name} — đã có, giữ nguyên (dùng --ghi-de nếu muốn tạo lại)")
    else:
        f_ks.write_text(json.dumps(ban_ghi, ensure_ascii=False, indent=2), encoding="utf-8")

    thieu = [x for x in ["u_linh.pt", "giong_ong_gia.pt", "ke.pt", "tran_thy.pt",
                         "giong_nu_tre.pt", "giong_trai_tre.pt", "giong_tre_em.pt"]
             if x not in [p.name for p in ds]]
    print(f"\n✅ {len(ds)} tệp · {tong / 1024:.2f} MB")
    print(f"   → {pt_dir.relative_to(GOC)}/SHA256SUMS")
    print(f"   → {(nguon / 'giong_pt.json').relative_to(GOC)}")
    if thieu:
        print(f"⚠  Thiếu so với danh sách notebook v5: {thieu}")
    else:
        print("   ✅ Đủ 7 tên khớp notebook v5 (cell 3)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Dựng cây thư mục data/")
    ap.add_argument("--kiem", action="store_true", help="chỉ xem thư mục nào còn thiếu")
    ap.add_argument("--van-tay", action="store_true", help="ghi SHA256SUMS cho 7 tệp .pt")
    ap.add_argument("--ghi-de", action="store_true", help="ghi đè SHA256SUMS / giong_pt.json đã có")
    a = ap.parse_args()
    if a.van_tay:
        return van_tay(a.ghi_de)
    print(f"Dựng cây dữ liệu tại {D.relative_to(GOC)}/\n")
    rc = tao(a.kiem)
    if not a.kiem:
        print("\nBước tiếp:")
        print(f"  1. chép 7 tệp .pt vào  {D.relative_to(GOC)}/RAW/giong_pt/")
        print("  2. python tools/du_lieu/tao_cay_thu_muc.py --van-tay")
        print("  3. python tools/du_lieu/kiem_pt.py --thu-muc data/RAW/giong_pt")
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
