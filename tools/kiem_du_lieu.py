#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CỔNG G2–G7 — Kiểm bộ dữ liệu đã chốt.

    python tools/du_lieu/kiem_du_lieu.py --bo v1
    python tools/du_lieu/kiem_du_lieu.py --bo v1 --day-du        # giải mã 100% tệp
    python tools/du_lieu/kiem_du_lieu.py --bo v1 --json data/LOG/kiem_du_lieu.json

Mã thoát = số cổng CHẶN. Chỉ được chốt dữ liệu khi mã thoát = 0.
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
import random
import re
import unicodedata
from collections import Counter
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

GOC = Path(__file__).resolve().parents[2]
RE_DEM = re.compile(r"\d")


class Cong:
    def __init__(self) -> None:
        self.dong: list[dict] = []

    def them(self, ma: str, muc: str, noi_dung: str) -> None:
        self.dong.append({"ma": ma, "muc": muc, "noi_dung": noi_dung})

    def bao_cao(self) -> int:
        rong = max([len(d["ma"]) for d in self.dong] + [4])
        print("-" * 108)
        for d in self.dong:
            print(f"  {d['ma']:<{rong}}  {d['muc']:<9} {d['noi_dung']}")
        print("-" * 108)
        chan = sum(1 for d in self.dong if d["muc"] == "CHẶN")
        canh = sum(1 for d in self.dong if d["muc"] == "CẢNH BÁO")
        print(f"  CHẶN: {chan} · CẢNH BÁO: {canh} · ĐẠT: {sum(1 for d in self.dong if d['muc'] == 'OK')}")
        if chan:
            print("\n  ❌ CHƯA QUA — sửa các mục CHẶN rồi chạy lại. Không được chốt.")
        elif canh:
            _ma = ", ".join(d["ma"] for d in self.dong if d["muc"] == "CẢNH BÁO")
            print(f"\n  ⚠ QUA CỔNG KỸ THUẬT nhưng còn {canh} CẢNH BÁO ({_ma}).")
            print("    KHÔNG được chốt im lặng và KHÔNG được dẫn dòng này làm 'đã được phép'.")
            print("    Mỗi cảnh báo phải được giải trình trong báo cáo; người duyệt phải quyết.")
        else:
            print("\n  ✅ QUA CỔNG — không CHẶN, không CẢNH BÁO. Được phép chốt (DATA_v…) và báo cáo.")
        return chan


def kiem_manifest(c: Cong, bo: Path) -> pd.DataFrame | None:
    f = bo / "manifest.csv"
    if not f.exists():
        c.them("G2.1", "CHẶN", f"Không có {f.relative_to(GOC)} — chưa chạy lam_sach.py")
        return None
    try:
        df = pd.read_csv(f, encoding="utf-8-sig")
    except Exception as e:
        c.them("G2.1", "CHẶN", f"manifest.csv không đọc được ({type(e).__name__}): {e}")
        return None
    if df.empty:
        c.them("G2.1", "CHẶN", "manifest.csv rỗng — không có dòng nào đạt; xem manifest_loai.csv")
        return None
    cot_can = {"utt_id", "nguon", "nguoi_noi", "thoi_luong_giay", "tan_so_mau",
               "van_ban_chuan", "so_am_tiet", "tap", "sha256", "duong_dan"}
    thieu = cot_can - set(df.columns)
    if thieu:
        c.them("G2.2", "CHẶN", f"manifest thiếu cột: {sorted(thieu)}")
        return None
    c.them("G2.2", "OK", f"{len(df):,} dòng · {df['nguoi_noi'].nunique()} người nói · "
                          f"{df['thoi_luong_giay'].sum() / 3600:.2f} giờ")

    trung = int(df["utt_id"].duplicated().sum())
    c.them("G2.3", "OK" if trung == 0 else "CHẶN", f"utt_id trùng: {trung}")

    thieu_tep = [p for p in df["duong_dan"] if not (GOC / p).exists()]
    c.them("G2.4", "OK" if not thieu_tep else "CHẶN",
           f"tệp wav thiếu: {len(thieu_tep)}" + (f" — ví dụ {thieu_tep[0]}" if thieu_tep else ""))

    # văn bản: NFC + không còn chữ số + số âm tiết khớp
    sai_nfc = sum(1 for t in df["van_ban_chuan"] if unicodedata.normalize("NFC", str(t)) != str(t))
    con_so = int(df["van_ban_chuan"].astype(str).str.contains(RE_DEM).sum())
    dem_sai = 0
    for t, n in zip(df["van_ban_chuan"].astype(str), df["so_am_tiet"]):
        if len([w for w in re.findall(r"[^\W\d_]+", t, re.UNICODE)]) != int(n):
            dem_sai += 1
    c.them("G3.1", "OK" if sai_nfc == 0 else "CHẶN", f"văn bản chưa chuẩn NFC: {sai_nfc}")
    c.them("G3.2", "OK" if con_so == 0 else "CHẶN", f"văn bản còn chữ số: {con_so}")
    c.them("G3.3", "OK" if dem_sai == 0 else "CẢNH BÁO", f"cột so_am_tiet lệch thực tế: {dem_sai}")

    # giấy phép: mọi nguồn trong manifest phải có giấy khai sinh
    thieu_ks = []
    for n in sorted(df["nguon"].unique()):
        ks = GOC / "data" / "RAW" / "_nguon" / f"{n}.json"
        if not ks.exists():
            thieu_ks.append(n)
        else:
            j = json.loads(ks.read_text(encoding="utf-8"))
            if not str(j.get("giay_phep", "")).strip():
                thieu_ks.append(n)
    c.them("G4.1", "OK" if not thieu_ks else "CHẶN",
           "mọi nguồn có giấy phép" if not thieu_ks
           else f"nguồn thiếu giấy khai sinh/giấy phép: {thieu_ks}")

    # tỉ lệ loại
    tk = bo / "thong_ke.json"
    nhe_test = False
    if tk.exists():
        j = json.loads(tk.read_text(encoding="utf-8"))
        nhe_test = bool(j.get("nguong_test_nhe"))
        ti_le = j.get("ti_le_loai") or 0
        co_gt = (bo / "GIAI_TRINH.md").exists()
        muc = "OK" if ti_le <= 0.40 or co_gt else "CHẶN"
        c.them("G5.1", muc, f"tỉ lệ loại {ti_le:.1%}"
                            + ("" if ti_le <= 0.40 else (" · đã có GIAI_TRINH.md" if co_gt
                               else " · >40% mà chưa có GIAI_TRINH.md")))

    # chia tập: không rò rỉ người nói
    le = df.groupby("nguoi_noi")["tap"].nunique()
    ro_ri = int((le > 1).sum())
    c.them("G6.1", "OK" if ro_ri == 0 else "CHẶN", f"người nói nằm ở nhiều tập: {ro_ri}")
    tap = Counter(df["tap"])
    c.them("G6.2", "OK" if set(tap) <= {"train", "val", "test"} else "CHẶN",
           f"phân bố tập: {dict(tap)}")
    if df["nguoi_noi"].nunique() >= 5 and tap.get("test", 0) == 0:
        c.them("G6.3", "CẢNH BÁO", "có ≥5 người nói nhưng tập test rỗng")

    # G6.4 — VIVOS chia sẵn: 46 người `VIVOSSPKxx` = train, 19 người `VIVOSDEVxx` = test CHÍNH THỨC.
    # Chia băm ngẫu nhiên sẽ đẩy phần lớn VIVOSDEV vào train → mọi số liệu sau đó đều vô nghĩa.
    _ten = df["nguoi_noi"].astype(str)
    _dev = df[_ten.str.match(r"(?i)^VIVOSDEV\d+$")]
    if len(_dev):
        _sai = _dev[~_dev["tap"].astype(str).str.lower().eq("test")]
        c.them("G6.4", "OK" if _sai.empty else "CHẶN",
               f"giọng VIVOSDEV (test chính thức của VIVOS): {_dev['nguoi_noi'].nunique()} · "
               f"nằm ngoài tập test: {_sai['nguoi_noi'].nunique()}"
               + ("" if _sai.empty else "  → chạy lại lam_sach.py --chia-tap vivos"))

    # G6.5 — tập train rỗng: bộ dữ liệu không dùng để huấn luyện được
    if tap.get("train", 0) == 0 and len(df):
        c.them("G6.5", "CẢNH BÁO",
               "tập train RỖNG — bộ này chỉ dùng để đánh giá, không huấn luyện được "
               "(nếu cố ý thì ghi rõ trong báo cáo; thường là do chạy --gioi-han)")
    else:
        c.them("G6.5", "OK", f"tập train có {tap.get('train', 0):,} dòng")

    # G6.6 — tập test CHÍNH THỨC của VIVOS bị bào mòn: G6.4 chỉ kiểm "không lọt vào train",
    # không kiểm "còn đủ hay không". VIVOS có 19 giọng test; lọc mất 10 giọng thì G6.4 vẫn OK.
    _dev_c = df[_ten.str.match(r"(?i)^VIVOSDEV\d+$")]
    if len(_dev_c):
        n_dev = int(_dev_c["nguoi_noi"].nunique())
        c.them("G6.6", "OK" if n_dev >= 15 else "CẢNH BÁO",
               f"giọng test chính thức của VIVOS còn lại: {n_dev}/19"
               + ("" if n_dev >= 15 else " — tập đánh giá bị bào mòn, kết quả kém tin cậy"))

    # tốc độ âm tiết + thời lượng
    td = df["thoi_luong_giay"]
    _ghi_chu_nhe = (" · ⚠ giọng test dùng ngưỡng 1,0 s (--nguong-test-nhe, xem DECISIONS N11)"
                    if nhe_test else "")
    c.them("G7.1", "OK",
           f"thời lượng: min {td.min():.2f}s · trung vị {td.median():.2f}s · max {td.max():.2f}s{_ghi_chu_nhe}")
    tv = df["so_am_tiet"] / df["thoi_luong_giay"]
    c.them("G7.2", "OK" if 2.0 <= tv.median() <= 6.0 else "CẢNH BÁO",
           f"tốc độ âm tiết trung vị {tv.median():.2f}/giây (kỳ vọng 2–6)")
    return df


def kiem_tep_am_thanh(c: Cong, df: pd.DataFrame, day_du: bool, mau: int = 200) -> None:
    import soundfile as sf
    ds = list(df.index) if day_du else random.Random(42).sample(list(df.index), min(mau, len(df)))
    hong, lech_tan_so, lech_thoi_luong = [], [], 0
    for i in ds:
        r = df.loc[i]
        p = GOC / r["duong_dan"]
        try:
            info = sf.info(str(p))
        except Exception:
            hong.append(r["duong_dan"])
            continue
        if int(info.samplerate) != int(r["tan_so_mau"]):
            lech_tan_so.append(r["utt_id"])
        if abs(info.frames / info.samplerate - float(r["thoi_luong_giay"])) > 0.06:
            lech_thoi_luong += 1
    c.them("G2.5", "OK" if not hong else "CHẶN",
           f"giải mã {len(ds):,} tệp · hỏng {len(hong)}")
    c.them("G2.6", "OK" if not lech_tan_so else "CHẶN",
           f"tần số mẫu lệch manifest: {len(lech_tan_so)}")
    c.them("G2.7", "OK" if lech_thoi_luong == 0 else "CẢNH BÁO",
           f"thời lượng lệch >60 ms: {lech_thoi_luong}")


def kiem_dong_y(c: Cong) -> bool:
    """Đường .pt: chấp nhận DONG_Y_7_GIONG.md đủ 7 dòng thay cho ref_manifest.csv."""
    f = GOC / "data" / "REF" / "DONG_Y_7_GIONG.md"
    if not f.exists():
        return False
    MA_GIONG = ["U_LINH", "ONG_GIA", "KE", "TRAN_THY", "NU_TRE", "TRAI_TRE", "TRE_EM"]
    van_ban = f.read_text(encoding="utf-8")
    # đếm dòng bảng có chứa một mã giọng (bền hơn đếm dòng trừ tiêu đề)
    so_dong = len({ma for ma in MA_GIONG
                   if any(f"| {ma} |" in d or f"|{ma}|" in d.replace(" ", "")
                          for d in van_ban.splitlines())})
    if so_dong >= 7:
        c.them("G8.1", "OK",
               f"đường .pt: DONG_Y_7_GIONG.md có {so_dong} dòng giọng "
               f"(G8.1 CHỈ đếm dòng — cột người đọc xem G8.6, mức đồng ý xem G8.7)")

        # G8.6 / G8.7 — G8.1 đếm dòng là chưa đủ: bảng mẫu có sẵn nên đếm dòng luôn "đạt"
        # trong khi tên người đọc vẫn để trống. Đây chính là cửa hậu của luật "cấm agent tự điền".
        TRONG = {"", "-", "—", "<tên>", "<ten>", "tên", "ten", "người dùng", "nguoi dung",
                 "nhóm", "nhom", "agent", "khong_ro", "chưa điền", "chua dien", "..."}
        thieu_ten: list[str] = []
        thieu_muc: list[str] = []
        _ten_da: list[str] = []
        for dong_md in van_ban.splitlines():
            if not dong_md.lstrip().startswith("|"):
                continue
            o = [x.strip() for x in dong_md.strip().strip("|").split("|")]
            if len(o) < 7:
                continue
            ma_giong = o[1].strip("`* ")
            if ma_giong not in MA_GIONG:
                continue
            nguoi_doc = o[3].strip("`* ")                      # cột "Người đọc"
            muc = o[6].strip("`* ")                            # cột "Đồng ý"
            if nguoi_doc.lower() in TRONG:
                thieu_ten.append(ma_giong)
            elif nguoi_doc:
                _ten_da.append(nguoi_doc.lower())
            if not muc or muc.startswith("☐") or muc.lower() in TRONG:
                thieu_muc.append(ma_giong)

        if thieu_ten:
            c.them("G8.6", "CẢNH BÁO",
                   f"{len(thieu_ten)}/7 giọng CHƯA điền tên người đọc "
                   f"({', '.join(thieu_ten)}) — G1 vẫn MỞ, không được coi là đã xong")
        elif len(set(_ten_da)) == 1 and len(_ten_da) >= 3:
            # 7 giọng khác nhau mà cùng một tên → gần như chắc chắn là điền cho có
            c.them("G8.6", "CẢNH BÁO",
                   f"cả {len(_ten_da)} dòng cùng một tên ('{_ten_da[0]}') — "
                   f"7 giọng phải là 7 người khác nhau; kiểm lại tờ phiếu")
        else:
            c.them("G8.6", "OK",
                   f"7/7 dòng có tên người đọc ({len(set(_ten_da))} người khác nhau)")
        if thieu_muc:
            c.them("G8.7", "CẢNH BÁO",
                   f"{len(thieu_muc)}/7 giọng CHƯA ghi mức đồng ý A/B/C/X "
                   f"({', '.join(thieu_muc)})")
        else:
            c.them("G8.7", "OK", "7/7 dòng có mức đồng ý")

        muc_x = van_ban.count("| X |") + van_ban.count("X — không liên hệ")
        if muc_x:
            c.them("G8.5", "CẢNH BÁO",
                   f"{muc_x} giọng ở mức X (mất liên lạc) — chỉ dùng nội bộ, ghi rõ trong báo cáo")
        return True
    c.them("G8.1", "CHẶN", f"DONG_Y_7_GIONG.md chỉ có {so_dong} dòng (cần 7)")
    return True


def kiem_ref(c: Cong) -> None:
    f = GOC / "data" / "REF" / "ref_manifest.csv"
    if not f.exists():
        if kiem_dong_y(c):
            return
        c.them("G8.1", "CẢNH BÁO",
               "chưa có data/REF/ref_manifest.csv và chưa có DONG_Y_7_GIONG.md — Pha A chưa xong")
        return
    df = pd.read_csv(f, encoding="utf-8-sig")
    so_giong = int(df["nguoi_noi"].nunique()) if "nguoi_noi" in df.columns else 0
    c.them("G8.1", "OK" if so_giong >= 7 else "CHẶN",
           f"giọng tham chiếu: {so_giong} (cần ≥7) · {len(df)} clip")
    sai_dai = df[~df["thoi_luong_giay"].between(3.0, 10.0)]
    c.them("G8.2", "OK" if sai_dai.empty else "CHẶN",
           f"clip ngoài 3–10 giây: {len(sai_dai)}")
    thieu_dong_y = df[~df["dong_y"].astype(str).str.lower().isin(["co", "có", "true", "1"])]
    c.them("G8.3", "OK" if thieu_dong_y.empty else "CHẶN",
           f"clip thiếu đồng ý của người đọc: {len(thieu_dong_y)}")
    thieu_text = df["van_ban"].isna() | (df["van_ban"].astype(str).str.strip() == "")
    c.them("G8.4", "OK" if not thieu_text.any() else "CHẶN",
           f"clip thiếu lời thoại: {int(thieu_text.sum())}")


def kiem_dung_luong(c: Cong, tran_mb: float = 100.0) -> None:
    """G10 — kho bài nộp phải < 100 MB, KHÔNG tính data/ (dữ liệu không đi kèm)."""
    bo_qua = {"data", ".git", ".cache", ".venv", "__pycache__", "node_modules"}
    tong, so = 0, 0
    for p in GOC.rglob("*"):
        if not p.is_file():
            continue
        if any(x in bo_qua for x in p.relative_to(GOC).parts):
            continue
        try:
            tong += p.stat().st_size
            so += 1
        except OSError:
            pass
    mb = tong / 1024 ** 2
    c.them("G10", "OK" if mb <= tran_mb else "CHẶN",
           f"kho bài nộp (trừ data/): {mb:.1f} MB trong {so} tệp "
           f"(trần {tran_mb:.0f} MB)")
    d = GOC / "data"
    if d.exists():
        tong_d = sum(f.stat().st_size for f in d.rglob("*") if f.is_file())
        c.them("G10b", "OK", f"data/ (không tính vào kho bài nộp): {tong_d / 1024 ** 2:.0f} MB")


def main() -> int:
    ap = argparse.ArgumentParser(description="Kiểm bộ dữ liệu đã chốt")
    ap.add_argument("--bo", default="v1", help="tên bộ trong data/SACH")
    ap.add_argument("--day-du", action="store_true", help="giải mã 100%% tệp (chậm)")
    ap.add_argument("--json", default="", help="ghi báo cáo JSON")
    a = ap.parse_args()

    bo = GOC / "data" / "SACH" / a.bo
    print("=" * 108)
    print(f"  KIỂM DỮ LIỆU — bộ '{a.bo}' · {bo.relative_to(GOC)}")
    print("=" * 108)
    c = Cong()
    df = kiem_manifest(c, bo)
    if df is not None and len(df):
        kiem_tep_am_thanh(c, df, a.day_du)
    kiem_ref(c)
    kiem_dung_luong(c)
    so_chan = c.bao_cao()

    if a.json:
        ra = Path(a.json) if Path(a.json).is_absolute() else GOC / a.json
        ra.parent.mkdir(parents=True, exist_ok=True)
        ra.write_text(json.dumps({
            "bo": a.bo, "thoi_diem": datetime.now().isoformat(timespec="seconds"),
            "so_chan": so_chan, "dong": c.dong,
        }, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"  Đã ghi: {ra.relative_to(GOC)}")
    return min(so_chan, 120)


if __name__ == "__main__":
    raise SystemExit(main())
