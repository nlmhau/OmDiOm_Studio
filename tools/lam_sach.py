#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A2 — LÀM SẠCH & LỌC: từ dữ liệu thô → bộ dữ liệu chốt (manifest + wav đã chuẩn hoá).

Chạy:
    python tools/du_lieu/lam_sach.py --tu-kiem
    python tools/du_lieu/lam_sach.py --mau                       # xuất manifest mẫu
    python tools/du_lieu/lam_sach.py --tho data/RAW/_manifest_tho.csv --ten-bo v1 --thu-kho
    python tools/du_lieu/lam_sach.py --tho data/RAW/_manifest_tho.csv --ten-bo v1
    python tools/du_lieu/lam_sach.py --kaldi data/RAW/vivos --ten-bo v1

Đầu vào (manifest thô, CSV, UTF-8):
    duong_dan   (bắt buộc) đường dẫn tới tệp âm thanh
    van_ban     (bắt buộc) lời thoại gốc
    nguon       (tuỳ chọn) mặc định "khong_ro"
    nguoi_noi   (tuỳ chọn) mặc định lấy tên thư mục cha
    gioi_tinh   (tuỳ chọn) nam / nu / khong_ro
    vung_mien   (tuỳ chọn) bac / trung / nam / khong_ro

Đầu ra (mặc định data/SACH/<ten-bo>/):
    wav/<nguon>/<nguoi_noi>/<utt_id>.wav   PCM 16-bit, mono, giữ tần số gốc
    manifest.csv            các dòng ĐẠT
    manifest_loai.csv       các dòng BỊ LOẠI + lý do (không bao giờ xoá mù)
    thong_ke.json           số liệu trước/sau, phân bố, cảnh báo
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
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
import soundfile as sf

GOC = Path(__file__).resolve().parents[2]

# ══════════════════════════════════════════════════════════════════════
# NGƯỠNG CHỐT — đổi phải ghi vào DECISIONS.md
# ══════════════════════════════════════════════════════════════════════
NGUONG = {
    "thoi_luong_min": 2.0,      # giây
    "thoi_luong_max": 20.0,     # giây
    "rms_min_dbfs": -45.0,
    "rms_max_dbfs": -8.0,
    "ti_le_noi_min": 0.35,      # tỉ lệ khung có tiếng nói sau khi cắt
    "ti_le_am_tiet_min": 2.0,   # âm tiết/giây
    "ti_le_am_tiet_max": 8.0,
    "lech_toc_do_max": 0.35,    # lệch so với trung vị toàn bộ, tính tỉ lệ
    "am_tiet_min": 4,
    "am_tiet_max": 120,
    "tan_so_toi_da": 24000,     # > mức này thì hạ xuống 24 kHz
    "toi_thieu_cau_moi_nguoi": 20,
    "toi_thieu_giay_moi_nguoi": 90.0,
    "tran_giay_moi_nguoi": 1800.0,   # 30 phút/người → cân bằng giọng
    "tran_lap_van_ban": 3,      # cùng một câu được tối đa 3 giọng đọc
}

CHU_SO = ["không", "một", "hai", "ba", "bốn", "năm", "sáu", "bảy", "tám", "chín"]
DON_VI = ["", "nghìn", "triệu", "tỷ", "nghìn tỷ", "triệu tỷ"]

CHU_CAI = ("aàáảãạăằắẳẵặâầấẩẫậeèéẻẽẹêềếểễệiìíỉĩịoòóỏõọôồốổỗộơờớởỡợ"
           "uùúủũụưừứửữựyỳýỷỹỵbcdđghklmnpqrstvx")
CHU_CAI = CHU_CAI + CHU_CAI.upper()
RE_TOKEN = re.compile(r"[^\W\d_]+", re.UNICODE)
RE_URL = re.compile(r"(https?://\S+|www\.\S+)", re.I)
RE_EMAIL = re.compile(r"\S+@\S+\.\S+")
RE_HTML = re.compile(r"<[^>]{1,200}>")
RE_SO = re.compile(r"\d[\d.,]*%?")


# ══════════════════════════════════════════════════════════════════════
# ĐỌC SỐ TIẾNG VIỆT
# ══════════════════════════════════════════════════════════════════════
def _doc_3(n: int, day_du: bool = False) -> str:
    """Đọc số 0..999. day_du=True → luôn đọc 'không trăm' khi thiếu hàng trăm."""
    tram, du = divmod(n, 100)
    chuc, dv = divmod(du, 10)
    out: list[str] = []
    if tram > 0 or (day_du and (chuc or dv)):
        out.append(f"{CHU_SO[tram]} trăm")
    if chuc == 0:
        if dv > 0:
            if (tram > 0 or day_du):
                out.append("lẻ")
            out.append(CHU_SO[dv])
    elif chuc == 1:
        out.append("mười")
        if dv == 5:
            out.append("lăm")
        elif dv > 0:
            out.append(CHU_SO[dv])
    else:
        out.append(f"{CHU_SO[chuc]} mươi")
        if dv == 1:
            out.append("mốt")
        elif dv == 5:
            out.append("lăm")
        elif dv > 0:
            out.append(CHU_SO[dv])
    return " ".join(out)


def doc_so(n: int) -> str:
    """Đọc số nguyên không âm thành chữ tiếng Việt."""
    if n == 0:
        return "không"
    nhom: list[int] = []
    while n > 0:
        n, du = divmod(n, 1000)
        nhom.append(du)
    if len(nhom) > len(DON_VI):
        return " ".join(CHU_SO[int(c)] for c in str(n))   # quá lớn → đọc từng chữ số
    phan: list[str] = []
    for i in range(len(nhom) - 1, -1, -1):
        gia_tri = nhom[i]
        if gia_tri == 0:
            continue                       # nhóm 0 thì bỏ hẳn (1 000 000 → "một triệu")
        phan.append(_doc_3(gia_tri, day_du=bool(phan) and gia_tri < 100))
        if DON_VI[i]:
            phan.append(DON_VI[i])
    return " ".join(x for x in phan if x)


def _doc_so_thap_phan(chuoi: str) -> str:
    """'1,5' → 'một phẩy năm'; '0,384' → 'không phẩy ba tám bốn'."""
    chuoi = chuoi.replace(".", ",")
    nguyen, _, le = chuoi.partition(",")
    nguyen = nguyen or "0"
    ra = doc_so(int(nguyen))
    if le:
        ra += " phẩy " + " ".join(CHU_SO[int(c)] for c in le if c.isdigit())
    return ra


DON_VI_DO = [
    (r"km\s*2|km²", "ki lô mét vuông"), (r"m\s*2|m²", "mét vuông"),
    (r"km", "ki lô mét"), (r"kg", "ki lô gam"), (r"cm", "xen ti mét"),
    (r"mm", "mi li mét"), (r"ml", "mi li lít"), (r"\blít\b", "lít"),
]


def thay_don_vi(text: str) -> str:
    for mau, chu in DON_VI_DO:
        text = re.sub(rf"(?<![\w]){mau}(?![\w])", f" {chu} ", text, flags=re.I)
    return re.sub(r"\s+", " ", text)


def thay_so(text: str) -> str:
    """Thay mọi cụm số trong câu bằng chữ tiếng Việt."""
    def _thay(m: re.Match) -> str:
        goc = m.group(0)
        la_phan_tram = goc.endswith("%")
        goc = goc.rstrip("%")
        # 1.234.567 → bỏ dấu chấm ngăn nghìn
        if re.fullmatch(r"\d{1,3}(\.\d{3})+", goc):
            goc = goc.replace(".", "")
        if re.fullmatch(r"\d+(,\d+)?", goc) or re.fullmatch(r"\d+(\.\d+)?", goc):
            ra = _doc_so_thap_phan(goc)
        else:
            ra = " ".join(CHU_SO[int(c)] if c.isdigit() else c for c in goc)
        return ra + (" phần trăm" if la_phan_tram else "")
    return RE_SO.sub(_thay, text)


# ══════════════════════════════════════════════════════════════════════
# CHUẨN HOÁ VĂN BẢN
# ══════════════════════════════════════════════════════════════════════
GIU_CHU_HOA = False          # --giu-chu-hoa đặt thành True
CACH_CHIA = 'tu-dong'        # --chia-tap {tu-dong,hash,vivos}
NGUONG_TEST_NHE = False      # --nguong-test-nhe: nới ngưỡng RIÊNG cho giọng test VIVOS

# Bản gốc VIVOS viết HOA toàn bộ nên KHÔNG có thông tin chữ hoa để khôi phục.
# Danh sách dưới đây chỉ để tên riêng phổ biến không bị viết thường trong báo cáo
# — đây là QUY ƯỚC của nhóm, không phải dữ liệu gốc. Muốn tắt: --giu-chu-hoa.
TEN_RIENG = [
    "hà nội", "hồ chí minh", "hà tây", "hải phòng", "đà nẵng", "cần thơ", "huế",
    "nha trang", "đà lạt", "vũng tàu", "quy nhơn", "biên hòa", "thủ đức", "bình dương",
    "hạ long", "phú quốc", "buôn ma thuột", "điện biên phủ", "việt nam", "sài gòn",
    "tây nguyên", "nam định", "thái nguyên", "thanh hóa", "nghệ an", "quảng ninh",
    "đồng nai", "long an", "hậu giang", "an giang", "kiên giang", "bình định",
]


def _hoa_ten_rieng(t: str) -> str:
    """'hà nội' → 'Hà Nội' (chỉ dùng sau khi đã hạ chữ hoa)."""
    for ten in TEN_RIENG:
        t = re.sub(rf"(?<!\w){re.escape(ten)}(?!\w)", ten.title(), t)
    return t


def ha_chu_hoa(t: str) -> tuple[str, bool]:
    """Chuỗi TOÀN CHỮ HOA (VIVOS/Kaldi ghi kiểu 'KHÁCH SẠN') → hoa câu.

    Chỉ đổi khi ≥90 % chữ cái là chữ HOA và chuỗi đủ dài (≥12 chữ cái), nên câu
    viết thường bình thường không bị chạm tới. → (chuỗi, đã_đổi)
    """
    chu = [c for c in t if c.isalpha()]
    if len(chu) < 12:
        return t, False
    if sum(1 for c in chu if c.isupper()) / len(chu) < 0.90:
        return t, False
    ra: list[str] = []
    dau_cau = True
    for c in t.lower():
        if dau_cau and c.isalpha():
            ra.append(c.upper())
            dau_cau = False
        else:
            ra.append(c)
            if c in ".!?":
                dau_cau = True
    return _hoa_ten_rieng("".join(ra)), True


def chuan_hoa_van_ban(tho: str) -> tuple[str, list[str]]:
    """→ (văn bản chuẩn, danh sách cảnh báo). Không bao giờ ném lỗi."""
    canh_bao: list[str] = []
    t = unicodedata.normalize("NFC", str(tho))
    if RE_URL.search(t):
        canh_bao.append("bo_url")
    if RE_EMAIL.search(t):
        canh_bao.append("bo_email")
    t = RE_HTML.sub(" ", t)
    t = RE_URL.sub(" ", t)
    t = RE_EMAIL.sub(" ", t)
    # ký tự điều khiển / định dạng / ký hiệu (emoji…) → bỏ
    giu: list[str] = []
    for ch in t:
        loai = unicodedata.category(ch)
        if loai in ("Cc", "Cf", "Cs", "Co", "So", "Sk", "Cn"):
            giu.append(" ")
        else:
            giu.append(ch)
    t = "".join(giu)
    t = (t.replace("“", "").replace("”", "").replace("‘", "").replace("’", "")
          .replace("\u00a0", " ").replace("…", " ").replace("–", " ").replace("—", " "))
    if not GIU_CHU_HOA:
        t, doi = ha_chu_hoa(t)
        if doi:
            canh_bao.append("ha_chu_hoa")
    t = thay_so(t)
    t = thay_don_vi(t)
    t = re.sub(r"[^0-9A-Za-zÀ-ỹ\s.,!?;:'\-]", " ", t)   # chỉ giữ chữ + dấu câu cơ bản
    t = re.sub(r"\s+", " ", t).strip()
    t = re.sub(r"\s+([.,!?;:])", r"\1", t)
    return t, canh_bao


def tach_am_tiet(text: str) -> list[str]:
    return [w for w in RE_TOKEN.findall(text) if w]


def la_am_tiet_viet(w: str) -> bool:
    return all(c in CHU_CAI for c in w)


# ══════════════════════════════════════════════════════════════════════
# XỬ LÝ ÂM THANH
# ══════════════════════════════════════════════════════════════════════
def doc_audio(p: Path) -> tuple[np.ndarray, int]:
    y, sr = sf.read(str(p), dtype="float32", always_2d=False)
    if getattr(y, "ndim", 1) > 1:
        y = y.mean(axis=1)
    return np.asarray(y, dtype=np.float32), int(sr)


def cat_im_lang(y: np.ndarray, sr: int, khung: float = 0.02, buoc: float = 0.01,
                nguong_tuong_doi: float = 0.03) -> tuple[np.ndarray, float, float]:
    """Cắt im lặng đầu/cuối. → (tín hiệu đã cắt, tỉ lệ khung có tiếng, giây bị cắt mỗi đầu)."""
    n_khung = int(khung * sr)
    n_buoc = max(1, int(buoc * sr))
    if len(y) < n_khung * 2:
        return y, 1.0, 0.0
    so_khung = 1 + (len(y) - n_khung) // n_buoc
    rms = np.empty(so_khung, dtype=np.float32)
    for i in range(so_khung):
        doan = y[i * n_buoc: i * n_buoc + n_khung]
        rms[i] = float(np.sqrt(np.mean(doan * doan) + 1e-12))
    dinh = float(rms.max()) or 1e-9
    nguong = max(dinh * nguong_tuong_doi, 10 ** (-45 / 20))
    co = np.where(rms > nguong)[0]
    if len(co) == 0:
        return y, 0.0, 0.0
    dau, cuoi = int(co[0]) * n_buoc, min(len(y), (int(co[-1]) + 1) * n_buoc + n_khung)
    pad = int(0.10 * sr)
    dau, cuoi = max(0, dau - pad), min(len(y), cuoi + pad)
    return y[dau:cuoi], float(len(co) / so_khung), dau / sr


def ha_tan_so(y: np.ndarray, sr: int, dich: int = 24000) -> tuple[np.ndarray, int, bool]:
    if sr <= dich:
        return y, sr, False          # KHÔNG nâng tần số giả
    try:
        import librosa
        return librosa.resample(y, orig_sr=sr, target_sr=dich), dich, True
    except Exception:
        return y, sr, False


def rms_dbfs(y: np.ndarray) -> float:
    if len(y) == 0:
        return -120.0
    return 20 * float(np.log10(max(float(np.sqrt(np.mean(y * y))), 1e-12)))


# ══════════════════════════════════════════════════════════════════════
# ĐỌC ĐẦU VÀO
# ══════════════════════════════════════════════════════════════════════
def _sph_sang_wav(p: Path) -> Path:
    """`.sph` → wav 16 kHz mono cạnh thư mục `wav/<SPK>/`. Dùng chung bộ giải mã với nap_vivos."""
    import sys as _s
    if str(Path(__file__).resolve().parent) not in _s.path:
        _s.path.insert(0, str(Path(__file__).resolve().parent))
    from nap_vivos import doc_sph                      # noqa: PLC0415
    ad = doc_sph(p.read_bytes())
    if ad is None or len(ad[0]) == 0:
        return p                                        # để nguyên, xu_ly sẽ loại kèm lý do
    y, sr = ad
    ra = p.parent.parent.parent / "wav" / p.parent.name / f"{p.stem}.wav"
    ra.parent.mkdir(parents=True, exist_ok=True)
    sf.write(str(ra), y, int(sr), subtype="PCM_16")
    return ra


def doc_genders(thu_muc: Path) -> dict[str, str]:
    """genders.txt (Kaldi spk2gender) → {'VIVOSSPK01': 'nam', ...}"""
    doi = {"m": "nam", "f": "nu", "nam": "nam", "nu": "nu"}
    ra: dict[str, str] = {}
    for ten in ("genders.txt", "spk2gender"):
        for f in thu_muc.rglob(ten):
            for dong in f.read_text(encoding="utf-8", errors="replace").splitlines():
                phan = dong.split()
                if len(phan) >= 2:
                    ra[phan[0]] = doi.get(phan[1].strip().lower(), "khong_ro")
    return ra


def doc_theo_kaldi(thu_muc: Path, nguon: str) -> pd.DataFrame:
    """Bố cục VIVOS gốc: <dir>/prompts.txt + <dir>/waves/<SPK>/*.wav (hoặc .sph)."""
    prompts = thu_muc / "prompts.txt"
    if not prompts.exists():
        ds = sorted(thu_muc.rglob("prompts.txt"))
        if ds:
            prompts = ds[0]
            thu_muc = prompts.parent
        else:
            raise SystemExit(f"❌ Không thấy prompts.txt trong {thu_muc}. "
                             f"Với dữ liệu dạng tar.gz, chạy trước: "
                             f"python tools/du_lieu/nap_vivos.py")
    genders = doc_genders(thu_muc)
    dong = []
    for dong_txt in prompts.read_text(encoding="utf-8", errors="replace").splitlines():
        if not dong_txt.strip():
            continue
        ma, _, cau = dong_txt.partition(" ")
        spk = ma.split("/")[0]
        f = thu_muc / "waves" / spk / f"{ma.split('/')[-1]}.wav"
        if not f.exists():
            f_sph = f.with_suffix(".sph")
            if f_sph.exists():
                f_wav = _sph_sang_wav(f_sph)
                if f_wav.suffix == ".sph":
                    # không giải mã được → vẫn ghi lại để xu_ly loại kèm lý do, không xoá mù
                    dong.append({"duong_dan": str(f_sph), "van_ban": cau.strip(),
                                 "nguoi_noi": spk, "nguon": nguon,
                                 "gioi_tinh": genders.get(spk, "khong_ro"),
                                 "vung_mien": "khong_ro"})
                    continue
                f = f_wav
            else:
                continue
        dong.append({"duong_dan": str(f), "van_ban": cau.strip(),
                     "nguoi_noi": spk, "nguon": nguon,
                     "gioi_tinh": genders.get(spk, "khong_ro"),
                     "vung_mien": "khong_ro"})
    return pd.DataFrame(dong)


def xuat_mau(ra: Path) -> None:
    mau = pd.DataFrame([
        {"duong_dan": "data/RAW/vivos/waves/VIVOSSPK01/0001.wav",
         "van_ban": "Hôm nay trời đẹp, chúng tôi đi dạo ven sông.",
         "nguon": "vivos", "nguoi_noi": "VIVOSSPK01",
         "gioi_tinh": "nam", "vung_mien": "bac"},
    ])
    ra.parent.mkdir(parents=True, exist_ok=True)
    mau.to_csv(ra, index=False, encoding="utf-8-sig")
    print(f"Đã ghi manifest mẫu: {ra}")


# ══════════════════════════════════════════════════════════════════════
# PIPELINE
# ══════════════════════════════════════════════════════════════════════
def _so(v, mac_dinh=float("nan")) -> float:
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return mac_dinh
    try:
        return float(v)
    except (TypeError, ValueError):
        return mac_dinh


def _dem(d: dict) -> Counter:
    return Counter(d.get("ly_do") or [])


def xu_ly(df: pd.DataFrame, ra: Path, ten_bo: str, thu_kho: bool = False) -> dict:
    N = NGUONG
    tot: list[dict] = []
    loai: list[dict] = []
    dem_ly_do: Counter = Counter()
    tong_tep_giay = 0.0        # tổng giây của TỆP GỐC (chưa cắt im lặng) — mọi dòng đọc được
    tong_goc_giay = 0.0        # tổng giây SAU khi cắt im lặng — mọi dòng đọc được, kể cả dòng bị loại
    sha_da_gap: dict[str, str] = {}
    text_da_gap: dict[tuple[str, str], str] = {}
    dem_text: Counter = Counter()

    # người nói thuộc tập test chính thức (VIVOSDEV) — xác định TRƯỚC khi lọc
    _re_dev = re.compile(r"^VIVOSDEV\d+$", re.IGNORECASE)
    _la_test = (lambda n: bool(_re_dev.match(str(n)))) if NGUONG_TEST_NHE else (lambda n: False)
    if NGUONG_TEST_NHE:
        print("  ⚠ ĐANG BẬT --nguong-test-nhe: giọng VIVOSDEV dùng ngưỡng nhẹ hơn (≥1,0 giây, "
              "không áp mức tối thiểu mỗi người).")
        print("    Chỉ hợp lệ khi VIVOS dùng làm MỐC ĐO; ghi quyết định này vào DECISIONS.md.")

    for idx, r in df.iterrows():
        ban_ghi = {
            "duong_dan_goc": str(r.get("duong_dan", "")),
            "van_ban_goc": str(r.get("van_ban", "")),
            "nguon": str(r.get("nguon") or "khong_ro"),
            "nguoi_noi": str(r.get("nguoi_noi") or Path(str(r.get("duong_dan", ""))).parent.name or "khong_ro"),
            "gioi_tinh": str(r.get("gioi_tinh") or "khong_ro"),
            "vung_mien": str(r.get("vung_mien") or "khong_ro"),
        }
        ly_do: list[str] = []
        p = Path(ban_ghi["duong_dan_goc"])
        if not p.is_absolute():
            p = GOC / p
        if not p.exists():
            ly_do.append("khong_thay_tep")
            loai.append({**ban_ghi, "ly_do": ";".join(ly_do)})
            dem_ly_do.update(ly_do)
            continue

        van_ban, canh_bao = chuan_hoa_van_ban(ban_ghi["van_ban_goc"])
        am_tiet = tach_am_tiet(van_ban)
        if not van_ban:
            ly_do.append("van_ban_rong")
        elif len(am_tiet) < N["am_tiet_min"]:
            ly_do.append("van_ban_qua_ngan")
        elif len(am_tiet) > N["am_tiet_max"]:
            ly_do.append("van_ban_qua_dai")
        elif not all(la_am_tiet_viet(w) for w in am_tiet):
            ly_do.append("co_ky_tu_la")

        try:
            y, sr = doc_audio(p)
        except Exception:
            ly_do.append("khong_doc_duoc")
            y = None
        if y is not None:
            if len(y) == 0:
                ly_do.append("tep_rong")
            else:
                dinh = float(np.max(np.abs(y)))
                tong_tep_giay += len(y) / sr
                y2, ti_le_noi, giay_cat = cat_im_lang(y, sr)
                dur = len(y2) / sr
                tong_goc_giay += dur
                rms = rms_dbfs(y2)
                if dinh >= 0.999:
                    ly_do.append("bao_hoa")
                if rms < N["rms_min_dbfs"]:
                    ly_do.append("qua_nho")
                elif rms > N["rms_max_dbfs"]:
                    ly_do.append("qua_to")
                if ti_le_noi < N["ti_le_noi_min"]:
                    ly_do.append("im_lang")
                _dur_min = 1.0 if _la_test(ban_ghi["nguoi_noi"]) else N["thoi_luong_min"]
                if dur < _dur_min:
                    ly_do.append("qua_ngan")
                elif dur > N["thoi_luong_max"]:
                    ly_do.append("qua_dai")
                toc_do = len(am_tiet) / dur if dur > 0 else 0.0
                if not (N["ti_le_am_tiet_min"] <= toc_do <= N["ti_le_am_tiet_max"]):
                    ly_do.append("toc_do_bat_thuong")
                sha = hashlib.sha256(p.read_bytes()).hexdigest()[:16]
                if sha in sha_da_gap:
                    ly_do.append("trung_tep")
                if van_ban:
                    if (ban_ghi["nguoi_noi"], van_ban) in text_da_gap:
                        ly_do.append("trung_van_ban_cung_nguoi")
                    elif dem_text[van_ban] >= N["tran_lap_van_ban"]:
                        ly_do.append("van_ban_lap_qua_nhieu")

                if not ly_do:
                    sha_da_gap[sha] = ban_ghi["duong_dan_goc"]
                    text_da_gap[(ban_ghi["nguoi_noi"], van_ban)] = ban_ghi["duong_dan_goc"]
                    dem_text[van_ban] += 1
                    tot.append({
                        **ban_ghi,
                        "van_ban_chuan": van_ban,
                        "canh_bao": ";".join(canh_bao),
                        "so_am_tiet": len(am_tiet),
                        "thoi_luong_giay": round(dur, 3),
                        "tan_so_mau": sr,
                        "rms_dbfs": round(rms, 1),
                        "ti_le_noi": round(ti_le_noi, 3),
                        "toc_do_am_tiet": round(toc_do, 2),
                        "giay_cat_dau": round(giay_cat, 3),
                        "sha256": hashlib.sha256(p.read_bytes()).hexdigest(),
                        "_y": y2,
                        "_sr": sr,
                        "_nguon_tep": p,
                    })
        if ly_do:
            loai.append({**ban_ghi, "ly_do": ";".join(dict.fromkeys(ly_do))})
            dem_ly_do.update(list(dict.fromkeys(ly_do)))

    # ── vòng 2: lọc theo tốc độ âm tiết trung vị ──────────────────────
    if tot:
        trung_vi = float(np.median([x["toc_do_am_tiet"] for x in tot]))
        giu = []
        for x in tot:
            lech = abs(x["toc_do_am_tiet"] / trung_vi - 1) if trung_vi else 0
            if lech > N["lech_toc_do_max"]:
                loai.append({
                    "duong_dan_goc": x["duong_dan_goc"], "van_ban_goc": x["van_ban_goc"],
                    "nguon": x["nguon"], "nguoi_noi": x["nguoi_noi"],
                    "gioi_tinh": x["gioi_tinh"], "vung_mien": x["vung_mien"],
                    "ly_do": "lech_toc_do",
                })
                dem_ly_do["lech_toc_do"] += 1
            else:
                giu.append(x)
        tot = giu
    else:
        trung_vi = 0.0

    # ── vòng 3: lọc người nói + trần thời lượng ───────────────────────
    theo_nguoi: dict[str, list[dict]] = defaultdict(list)
    for x in tot:
        theo_nguoi[x["nguoi_noi"]].append(x)
    truoc = len(tot)
    for nguoi, ds in list(theo_nguoi.items()):
        tong_giay = sum(x["thoi_luong_giay"] for x in ds)
        if _la_test(nguoi):
            nguong_cau, nguong_giay = 1, 0.0        # mốc đo: mỗi người chỉ cần ≥1 câu hợp lệ
        else:
            nguong_cau, nguong_giay = N["toi_thieu_cau_moi_nguoi"], N["toi_thieu_giay_moi_nguoi"]
        if len(ds) < nguong_cau or tong_giay < nguong_giay:
            for x in ds:
                loai.append({
                    "duong_dan_goc": x["duong_dan_goc"], "van_ban_goc": x["van_ban_goc"],
                    "nguon": x["nguon"], "nguoi_noi": x["nguoi_noi"],
                    "gioi_tinh": x["gioi_tinh"], "vung_mien": x["vung_mien"],
                    "ly_do": "nguoi_noi_qua_it_du_lieu",
                })
                dem_ly_do["nguoi_noi_qua_it_du_lieu"] += 1
            del theo_nguoi[nguoi]
            continue
        tong = 0.0
        giu = []
        for x in ds:
            if tong + x["thoi_luong_giay"] > N["tran_giay_moi_nguoi"]:
                loai.append({
                    "duong_dan_goc": x["duong_dan_goc"], "van_ban_goc": x["van_ban_goc"],
                    "nguon": x["nguon"], "nguoi_noi": x["nguoi_noi"],
                    "gioi_tinh": x["gioi_tinh"], "vung_mien": x["vung_mien"],
                    "ly_do": "vuot_tran_giay_moi_nguoi",
                })
                dem_ly_do["vuot_tran_giay_moi_nguoi"] += 1
            else:
                tong += x["thoi_luong_giay"]
                giu.append(x)
        theo_nguoi[nguoi] = giu
    tot = [x for ds in theo_nguoi.values() for x in ds]

    # ── chia tập theo NGƯỜI NÓI (không rò rỉ) ─────────────────────────
    nguoi_ds = sorted(theo_nguoi)
    _re_vivos = re.compile(r"^VIVOS(SPK|DEV)\d+$", re.IGNORECASE)
    _so_vivos = sum(1 for n in nguoi_ds if _re_vivos.match(n))
    _dung_vivos = (CACH_CHIA == "vivos") or (
        CACH_CHIA == "tu-dong" and bool(nguoi_ds) and _so_vivos / len(nguoi_ds) >= 0.80)

    if _dung_vivos:
        # VIVOS chia sẵn: 46 người `VIVOSSPKxx` = train, 19 người `VIVOSDEVxx` = test chính thức.
        # Băm ngẫu nhiên sẽ đẩy VIVOSDEV vào train → rò rỉ tập test chính thức của cả bộ.
        tap = {}
        for n in nguoi_ds:
            m = _re_vivos.match(n)
            tap[n] = "test" if (m and m.group(1).upper() == "DEV") else "train"
        so_dev = sum(1 for v in tap.values() if v == "test")
        so_spk = len(nguoi_ds) - so_dev
        cach_chia = f"vivos_goc__{so_spk}_SPK_train__{so_dev}_DEV_test__khong_co_val"
        print(f"  Chia tập theo VIVOS gốc: train {so_spk} người · test {so_dev} người "
              f"(VIVOS không có tập val chính thức)")
        if so_dev == 0:
            print("  ⚠ CẢNH BÁO: không thấy người nói VIVOSDEV* nào → tập test rỗng (G6.3 sẽ báo)")
    elif len(nguoi_ds) >= 5:
        # xếp theo băm md5 (tất định), rồi chia 10% test / 10% val / còn lại train
        nguoi_sap = sorted(nguoi_ds, key=lambda x: hashlib.md5(x.encode("utf-8")).hexdigest())
        n = len(nguoi_sap)
        n_test = max(1, round(0.10 * n))
        n_val = max(1, round(0.10 * n)) if n >= 10 else 0
        tap = {}
        for i, nguoi in enumerate(nguoi_sap):
            tap[nguoi] = ("test" if i < n_test
                          else "val" if i < n_test + n_val else "train")
        cach_chia = f"theo_nguoi_noi__{n_test}_test__{n_val}_val"
    else:
        # dưới 5 người nói: không thể chia test mà không rò rỉ → để tất cả train
        tap = {n: "train" for n in nguoi_ds}
        cach_chia = "khong_du_nguoi_noi__tat_ca_train"

    # ── cảnh báo tập rỗng: một bộ không có train (hoặc không có test) là bộ vô dụng ──
    _dem = Counter(tap.values())
    for _ten_tap, _nghia in (("train", "không huấn luyện được"),
                             ("test", "không đánh giá được")):
        if _dem.get(_ten_tap, 0) == 0:
            print(f"  ⚠ CẢNH BÁO: tập '{_ten_tap}' RỖNG → bộ dữ liệu {_nghia}.")
            print("    Thường do cắt bớt dữ liệu (--gioi-han / --gioi-han-nguoi). "
                  "Muốn số liệu thật: chạy lại KHÔNG có hai cờ đó.")

    # ── ghi kết quả ───────────────────────────────────────────────────
    dem_id: Counter = Counter()
    for x in sorted(tot, key=lambda z: (z["nguoi_noi"], z["sha256"])):
        dem_id[x["nguoi_noi"]] += 1
        x["utt_id"] = f"{x['nguon']}-{x['nguoi_noi']}-{dem_id[x['nguoi_noi']]:05d}"
        x["tap"] = tap.get(x["nguoi_noi"], "train")

    if not thu_kho:
        thu_muc_wav = ra / "wav"
        for x in tot:
            dich = thu_muc_wav / x["nguon"] / x["nguoi_noi"] / f"{x['utt_id']}.wav"
            dich.parent.mkdir(parents=True, exist_ok=True)
            y, sr, da_ha = ha_tan_so(x["_y"], x["_sr"])
            sf.write(str(dich), y, sr, subtype="PCM_16")
            x["duong_dan"] = str(dich.relative_to(GOC))
            x["tan_so_mau"] = sr
            x["da_ha_tan_so"] = bool(da_ha)

    cot = ["utt_id", "nguon", "nguoi_noi", "gioi_tinh", "vung_mien", "thoi_luong_giay",
           "tan_so_mau", "rms_dbfs", "ti_le_noi", "toc_do_am_tiet", "so_am_tiet",
           "van_ban_chuan", "van_ban_goc", "canh_bao", "tap", "sha256",
           "duong_dan", "duong_dan_goc"]
    df_tot = pd.DataFrame([{c: x.get(c, "") for c in cot} for x in tot], columns=cot)
    df_loai = pd.DataFrame(loai)

    # ── cảnh báo mâu thuẫn: loại ít dòng mà mất nhiều giờ = lý do loại có vấn đề ──
    if tong_goc_giay > 0 and len(df_tot):
        _giu_giay = float(df_tot["thoi_luong_giay"].sum())
        _tile_dong = len(loai) / len(df)
        _tile_gio = 1 - _giu_giay / tong_goc_giay
        if _tile_gio > _tile_dong + 0.05:
            print(f"  ⚠ CẢNH BÁO: loại {_tile_dong:.1%} số dòng nhưng mất {_tile_gio:.1%} thời lượng.")
            print(f"    Câu bị loại DÀI hơn câu giữ lại ({tong_goc_giay/max(len(df),1):.2f}s vs "
                  f"{_giu_giay/max(len(df_tot),1):.2f}s) — trái với lý do loại hàng đầu. "
                  f"Kiểm lại trước khi báo cáo con số giờ.")

    _tong_ly_do = sum(dem_ly_do.values())
    if _tong_ly_do > len(loai):
        print(f"  ℹ Tổng các lý do ({_tong_ly_do:,}) LỚN HƠN số dòng bị loại ({len(loai):,}) "
              f"vì một dòng có thể mắc nhiều lý do. Đừng cộng chúng lại thành 100 %.")

    # ── giọng test chính thức của VIVOS còn sống được bao nhiêu ──
    _r_v = re.compile(r"^VIVOSDEV\d+$", re.IGNORECASE)
    _con = sorted(theo_nguoi)          # theo_nguoi đã bị xoá các giọng không đủ điều kiện
    _dev_con = [n for n in _con if _r_v.match(n)]
    if _dev_con:
        print(f"  Giọng test chính thức của VIVOS còn lại: {len(_dev_con)}/19"
              + ("  ⚠" if len(_dev_con) < 15 else ""))

    thong_ke = {
        "ten_bo": ten_bo,
        "thoi_diem": datetime.now().isoformat(timespec="seconds"),
        "dau_vao": int(len(df)),
        "dat": int(len(df_tot)),
        "bi_loai": int(len(loai)),
        "ti_le_loai": round(len(loai) / len(df), 4) if len(df) else None,
        "ly_do_loai": dict(dem_ly_do.most_common()),
        "tong_gio": round(float(df_tot["thoi_luong_giay"].sum()) / 3600, 2) if len(df_tot) else 0.0,
        "tong_gio_tep": round(tong_tep_giay / 3600, 2),        # thời lượng TỆP GỐC, chưa cắt im lặng
        "tong_gio_truoc_loc": round(tong_goc_giay / 3600, 2),  # SAU khi cắt im lặng, trước khi lọc
        "tong_gio_goc": round(tong_goc_giay / 3600, 2),        # giữ tên cũ để không phá báo cáo đã viết
        "nguong_test_nhe": bool(NGUONG_TEST_NHE),
        "so_nguoi_noi": int(df_tot["nguoi_noi"].nunique()) if len(df_tot) else 0,
        "vi_sao_chia_tap": cach_chia,
        "tap": df_tot["tap"].value_counts().to_dict() if len(df_tot) else {},
        "toc_do_am_tiet_trung_vi": round(trung_vi, 2),
        "nguong": NGUONG,
        "thu_kho": bool(thu_kho),
    }

    if thu_kho:
        print(json.dumps(thong_ke, ensure_ascii=False, indent=2))
        print("\n(--thu-kho: KHÔNG ghi tệp nào)")
        return thong_ke

    ra.mkdir(parents=True, exist_ok=True)
    df_tot.to_csv(ra / "manifest.csv", index=False, encoding="utf-8-sig")
    df_loai.to_csv(ra / "manifest_loai.csv", index=False, encoding="utf-8-sig")
    (ra / "thong_ke.json").write_text(json.dumps(thong_ke, ensure_ascii=False, indent=2),
                                      encoding="utf-8")
    print(f"ĐẠT {len(df_tot):,} · LOẠI {len(loai):,} · {thong_ke['tong_gio']} giờ · "
          f"{thong_ke['so_nguoi_noi']} người nói")
    if len(df_tot) == 0:
        print("❌ KHÔNG dòng nào đạt. Xem cột ly_do trong manifest_loai.csv.")
        print("   Hay gặp: mỗi người nói < 20 câu (luật P1) hoặc audio < 2 giây (S4).")
        print("   Không tự nới ngưỡng — đọc DECISIONS.md và eval/eval_objective.py.")
    print(f"→ {ra.relative_to(GOC)}/manifest.csv")
    if len(df) and thong_ke["ti_le_loai"] > 0.40:
        print("⚠  Loại hơn 40 % số dòng — bắt buộc giải trình trong báo cáo (cổng G5).")
    return thong_ke


# ══════════════════════════════════════════════════════════════════════
# TỰ KIỂM
# ══════════════════════════════════════════════════════════════════════
def tu_kiem() -> int:
    ca = [
        (0, "không"), (5, "năm"), (10, "mười"), (11, "mười một"), (15, "mười lăm"),
        (21, "hai mươi mốt"), (25, "hai mươi lăm"), (100, "một trăm"),
        (101, "một trăm lẻ một"), (110, "một trăm mười"), (1000, "một nghìn"),
        (1005, "một nghìn không trăm lẻ năm"), (2026, "hai nghìn không trăm hai mươi sáu"),
        (1000000, "một triệu"),
        (1234567, "một triệu hai trăm ba mươi bốn nghìn năm trăm sáu mươi bảy"),
    ]
    hong = 0
    for n, mong_doi in ca:
        that = doc_so(n)
        if that != mong_doi:
            print(f"  ✗ {n}: '{that}' ≠ '{mong_doi}'")
            hong += 1
    van_ban_ca = [
        ("Giá là 15.000 đồng.", None),
        ("Năm 2026 có 12 tháng.", None),
        ("Tỉ lệ 0,384 rất thấp.", None),
        ("Xem https://example.com nhé!", None),
        ("Mua 2 kg gạo 😀", None),
        ("", None),
    ]
    for vb, _ in van_ban_ca:
        ra, cb = chuan_hoa_van_ban(vb)
        print(f"  · '{vb}' → '{ra}'  {('[' + ','.join(cb) + ']') if cb else ''}")
        if re.search(r"\d", ra):
            print(f"    ✗ còn chữ số trong đầu ra")
            hong += 1

    print("\n  Chữ HOA toàn chuỗi (kiểu VIVOS):")
    ca_hoa = [
        ("KHÁCH SẠN Ở HÀ NỘI RẤT ĐẸP VÀ SẠCH SẼ",
         "Khách sạn ở Hà Nội rất đẹp và sạch sẽ"),
        ("Hôm nay trời đẹp, chúng tôi đi dạo ven sông.",
         "Hôm nay trời đẹp, chúng tôi đi dạo ven sông."),   # KHÔNG được đổi
        ("Hà Nội", "Hà Nội"),                                # quá ngắn → không đổi
    ]
    for vao, mong in ca_hoa:
        ra, _cb = chuan_hoa_van_ban(vao)
        dat = ra == mong
        print(f"  {'·' if dat else '✗'} {vao[:46]!r} → {ra!r}")
        if not dat:
            print(f"      mong đợi: {mong!r}")
            hong += 1
    print(f"\n{'✅ TỰ KIỂM ĐẠT' if hong == 0 else f'❌ {hong} ca hỏng'}")
    return 1 if hong else 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Làm sạch & lọc dữ liệu cho Pha A")
    ap.add_argument("--tho", default="", help="manifest thô CSV")
    ap.add_argument("--kaldi", default="", help="thư mục kiểu Kaldi/VIVOS (prompts.txt + waves/)")
    ap.add_argument("--nguon", default="vivos", help="mã nguồn khi dùng --kaldi")
    ap.add_argument("--ten-bo", default="v1", help="tên bộ dữ liệu (thư mục con trong data/SACH)")
    ap.add_argument("--ra", default="", help="thư mục đích (mặc định data/SACH/<ten-bo>)")
    ap.add_argument("--thu-kho", action="store_true", help="chỉ tính, không ghi")
    ap.add_argument("--gioi-han", type=int, default=0,
                    help="chỉ xử lý N DÒNG đầu — CẮT GIỮA người nói, làm sai ngưỡng và chia tập. "
                         "Chỉ để đo tốc độ.")
    ap.add_argument("--gioi-han-nguoi", type=int, default=0,
                    help="chỉ xử lý N NGƯỜI NÓI đầu, giữ ĐỦ câu của họ — dùng cái này để thử thật")
    ap.add_argument("--mau", action="store_true", help="xuất manifest mẫu")
    ap.add_argument("--tu-kiem", action="store_true", help="chạy kiểm tra nội bộ")
    ap.add_argument("--giu-chu-hoa", action="store_true",
                    help="KHÔNG hạ chữ hoa toàn chuỗi (mặc định: 'KHÁCH SẠN' → 'Khách sạn')")
    ap.add_argument("--nguong-test-nhe", action="store_true",
                    help="giọng VIVOSDEV (tập test) chỉ cần ≥1,0 giây/câu và KHÔNG áp mức tối thiểu "
                         "≥20 câu / ≥90 giây. Dùng khi VIVOS là MỐC ĐO chứ không phải dữ liệu huấn luyện")
    ap.add_argument("--chia-tap", default="tu-dong", choices=["tu-dong", "hash", "vivos"],
                    help="cách chia train/val/test: tu-dong (mặc định, tự nhận VIVOS) · "
                         "hash (băm người nói) · vivos (đúng 46 SPK = train / 19 DEV = test)")
    a = ap.parse_args()

    global GIU_CHU_HOA, CACH_CHIA, NGUONG_TEST_NHE
    GIU_CHU_HOA = bool(a.giu_chu_hoa)
    CACH_CHIA = a.chia_tap
    NGUONG_TEST_NHE = bool(a.nguong_test_nhe)

    if a.tu_kiem:
        return tu_kiem()

    ra = Path(a.ra) if a.ra else GOC / "data" / "SACH" / a.ten_bo
    if a.mau:
        xuat_mau(GOC / "data" / "RAW" / "_manifest_tho_mau.csv")
        return 0

    if a.kaldi:
        df = doc_theo_kaldi(Path(a.kaldi), a.nguon)
        print(f"Đọc {len(df)} dòng từ bố cục Kaldi: {a.kaldi}")
    elif a.tho:
        p = Path(a.tho) if Path(a.tho).is_absolute() else GOC / a.tho
        df = pd.read_csv(p, encoding="utf-8-sig")
        print(f"Đọc {len(df)} dòng từ {p}")
    else:
        ap.print_help()
        return 1

    if a.gioi_han_nguoi:
        _tat_ca = list(dict.fromkeys(df["nguoi_noi"].astype(str)))
        _r = re.compile(r"^VIVOS(SPK|DEV)\d+$", re.IGNORECASE)
        _spk = [x for x in _tat_ca if (_r.match(x) and _r.match(x).group(1).upper() == "SPK")]
        _dev = [x for x in _tat_ca if (_r.match(x) and _r.match(x).group(1).upper() == "DEV")]
        if _spk and _dev and a.gioi_han_nguoi >= 2:
            # lấy mẫu theo đúng tỉ lệ gốc để smoke test vẫn có cả train lẫn test
            _n_spk = max(1, round(a.gioi_han_nguoi * len(_spk) / len(_tat_ca)))
            _n_dev = max(1, a.gioi_han_nguoi - _n_spk)
            _giu = _spk[:_n_spk] + _dev[:_n_dev]
            print(f"(mẫu thử {len(_giu)} người nói: {_n_spk} VIVOSSPK + {_n_dev} VIVOSDEV)")
        else:
            _giu = _tat_ca[: a.gioi_han_nguoi]
            print(f"(chỉ xử lý {len(_giu)} NGƯỜI NÓI đầu, giữ đủ câu của họ)")
        df = df[df["nguoi_noi"].astype(str).isin(_giu)].reset_index(drop=True)
        print(f"  giữ đủ câu của họ: {len(df)} dòng")

    if a.gioi_han:
        df = df.head(a.gioi_han)
        print(f"(giới hạn {a.gioi_han} dòng để thử)")
        print("  ⚠ --gioi-han CẮT GIỮA DỮ LIỆU: ngưỡng 'mỗi người nói' (≥20 câu, ≥90 giây) và")
        print("    phân chia train/val/test sẽ SAI. Chỉ dùng để đo tốc độ — KHÔNG đọc số từ lần chạy này.")
        print("    Muốn thử đúng: cắt theo NGƯỜI NÓI (chọn ra vài người rồi lấy toàn bộ câu của họ).")
    if df.empty:
        print("❌ Manifest rỗng.")
        return 1
    for cot in ("duong_dan", "van_ban"):
        if cot not in df.columns:
            print(f"❌ Manifest thiếu cột bắt buộc: {cot}")
            return 1

    xu_ly(df, ra, a.ten_bo, a.thu_kho)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
