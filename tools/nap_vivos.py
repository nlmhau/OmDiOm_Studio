#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A1.4b — VIVOS → WAV + manifest thô.  Hỗ trợ CẢ HAI dạng:

  (1) TAR.GZ  (bố cục Kaldi: vivos/{train,test}/prompts.txt + waves/<SPK>/*.sph|*.wav)
      — đây là dạng thật của AILAB-VNUHCM/vivos trên Hugging Face và của Zenodo.
  (2) PARQUET (nếu có) — dạng cũ, vẫn giữ để tương thích.

    python tools/du_lieu/nap_vivos.py --kiem                 # xem kho có gì, KHÔNG ghi
    python tools/du_lieu/nap_vivos.py                        # tự dò tar.gz hoặc parquet
    python tools/du_lieu/nap_vivos.py --tar data/RAW/vivos/data/vivos.tar.gz
    python tools/du_lieu/nap_vivos.py --gioi-han 500         # thử nhanh
    python tools/du_lieu/nap_vivos.py --chi-lap-danh-sach    # chỉ liệt kê thành phần tar

Đầu ra:
    data/RAW/vivos/wav/<nguoi_noi>/*.wav
    data/RAW/_manifest_tho.csv   (6 cột: duong_dan, van_ban, nguon, nguoi_noi, gioi_tinh, vung_mien)

⚠ QUAN TRỌNG: bản tar gốc của VIVOS chứa tệp **.sph** (NIST SPHERE, của Kaldi), KHÔNG phải .wav.
   `soundfile` KHÔNG đọc được .sph. Script có bộ đọc SPHERE THUẦN PYTHON (không cần
   ffmpeg/sox, không cần cài thêm gì) — ffmpeg/sox chỉ là dự phòng nếu định dạng lạ.
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
import io
import shutil
import subprocess
import tarfile
from pathlib import Path

import numpy as np
import pandas as pd
import soundfile as sf

GOC = Path(__file__).resolve().parents[2]
VIVOS = GOC / "data" / "RAW" / "vivos"
DUOI_AM_THANH = (".wav", ".sph", ".flac", ".mp3", ".opus", ".m4a")


# ══════════════════════════════════════════════════════════════════════
# Dò đầu vào
# ══════════════════════════════════════════════════════════════════════
def tim_tar(goc: Path) -> list[Path]:
    return sorted(list(goc.rglob("*.tar.gz")) + list(goc.rglob("*.tgz")))


def tim_parquet(goc: Path) -> list[Path]:
    return sorted(goc.rglob("*.parquet"))


def co_lenh(ten: str) -> bool:
    return shutil.which(ten) is not None


# ══════════════════════════════════════════════════════════════════════
# Đọc văn bản / giới tính kiểu Kaldi
# ══════════════════════════════════════════════════════════════════════
def doc_prompts(tar: tarfile.TarFile, ten: str) -> dict[str, str]:
    """prompts.txt: '<SPK>/<SPK>_R00X <câu>'  →  {'<SPK>_R00X': '<câu>'}"""
    ra: dict[str, str] = {}
    try:
        f = tar.extractfile(ten)
        if f is None:
            return ra
        for dong in f.read().decode("utf-8", errors="replace").splitlines():
            dong = dong.strip()
            if not dong:
                continue
            ma, _, cau = dong.partition(" ")
            ra[ma.split("/")[-1]] = cau.strip()
    except Exception:
        pass
    return ra


def doc_genders(tar: tarfile.TarFile, ten: str) -> dict[str, str]:
    """genders.txt (Kaldi spk2gender): '<SPK> <m|f>'  →  {'<SPK>': 'nam'|'nu'}"""
    doi = {"m": "nam", "f": "nu", "male": "nam", "female": "nu", "nam": "nam", "nu": "nu"}
    ra: dict[str, str] = {}
    try:
        f = tar.extractfile(ten)
        if f is None:
            return ra
        for dong in f.read().decode("utf-8", errors="replace").splitlines():
            phan = dong.split()
            if len(phan) >= 2:
                ra[phan[0]] = doi.get(phan[1].strip().lower(), "khong_ro")
    except Exception:
        pass
    return ra


# ══════════════════════════════════════════════════════════════════════
# .sph (NIST SPHERE) — đọc THUẦN PYTHON, không cần ffmpeg/sox
# ══════════════════════════════════════════════════════════════════════
def doc_sph(raw: bytes) -> tuple[np.ndarray, int] | None:
    """Giải mã NIST SPHERE → (mảng float32 mono trong [-1,1], sample_rate).

    Cấu trúc: 1.024 byte đầu là header ASCII dạng '<tên> [-i|-sN] <giá trị>\\n',
    phần còn lại là PCM thô. Kaldi/VIVOS dùng 16 kHz · 2 byte · PCM · big-endian ('10').
    Trả None nếu không phải SPHERE hoặc mã hoá không hỗ trợ (vd. gsm, shorten).
    """
    if len(raw) < 1028 or not raw.startswith(b"NIST_1A"):
        return None
    hdr = {}
    for dong in raw[:1024].split(b"\n"):
        phan = dong.decode("ascii", errors="replace").split()
        if len(phan) >= 3 and phan[1].startswith("-"):
            hdr[phan[0]] = phan[2]
    try:
        sr = int(hdr.get("sample_rate", "16000"))
        n_byte = int(hdr.get("sample_n_bytes", "2"))
        n_ch = int(hdr.get("channel_count", "1"))
        n_mau = int(hdr.get("sample_count", "0"))
    except ValueError:
        return None
    coding = str(hdr.get("sample_coding", "pcm")).lower()
    if "pcm" not in coding:
        return None                      # gsm / shorten / ulaw → để ffmpeg lo
    than = raw[1024:]
    if n_byte == 2:
        kieu = ">i2" if hdr.get("sample_byte_format", "01") == "10" else "<i2"
        x = np.frombuffer(than[: (len(than) // 2) * 2], dtype=np.dtype(kieu))
        y = (x.astype(np.float32) / 32768.0)
    elif n_byte == 4:
        kieu = ">i4" if hdr.get("sample_byte_format", "01") == "10" else "<i4"
        x = np.frombuffer(than[: (len(than) // 4) * 4], dtype=np.dtype(kieu))
        y = (x.astype(np.float32) / 2147483648.0)
    elif n_byte == 1:
        y = (np.frombuffer(than, dtype=np.uint8).astype(np.float32) - 128.0) / 128.0
    else:
        return None
    if n_mau > 0:
        y = y[:n_mau]
    if n_ch > 1:
        y = y[: (len(y) // n_ch) * n_ch].reshape(-1, n_ch).mean(axis=1)
    return np.ascontiguousarray(y, dtype=np.float32), sr


def chuyen_sang_wav(nguon: Path, dich: Path) -> tuple[bool, str]:
    """`.sph` → WAV 16-bit mono. Ưu tiên SPHERE thuần Python; chỉ khi lạ mới gọi ffmpeg/sox."""
    dich.parent.mkdir(parents=True, exist_ok=True)
    raw = nguon.read_bytes()

    ad = doc_sph(raw) if nguon.suffix.lower() == ".sph" else None
    if ad is not None and len(ad[0]) > 0:
        sf.write(str(dich), ad[0], int(ad[1]), subtype="PCM_16")
        return True, "python-sph"

    for lenh in (["ffmpeg", "-loglevel", "error", "-y", "-i", str(nguon),
                  "-ac", "1", "-c:a", "pcm_s16le", str(dich)],
                 ["sox", str(nguon), "-c", "1", str(dich)]):
        if not co_lenh(lenh[0]):
            continue
        r = subprocess.run(lenh, capture_output=True, text=True,
                           encoding="utf-8", errors="replace")
        if r.returncode == 0 and dich.exists() and dich.stat().st_size > 1000:
            return True, lenh[0]
    return False, "không đọc được .sph (không phải PCM) và không có ffmpeg/sox"



# ══════════════════════════════════════════════════════════════════════
# Đường 1: TAR.GZ
# ══════════════════════════════════════════════════════════════════════
def liet_ke_tar(p: Path, gioi_han: int = 40) -> None:
    with tarfile.open(p, "r:gz") as tar:
        ten = tar.getnames()
        am_thanh = [t for t in ten if t.lower().endswith(DUOI_AM_THANH)]
        duoi: dict[str, int] = {}
        for t in am_thanh:
            d = Path(t).suffix.lower()
            duoi[d] = duoi.get(d, 0) + 1
        print(f"  Tổng mục trong tar : {len(ten)}")
        print(f"  Tệp âm thanh       : {len(am_thanh)}  {duoi}")
        print(f"  Tệp văn bản/khác   :")
        for t in ten:
            if t.lower().endswith((".txt", ".md", "copying", ".lst")):
                print(f"    · {t}")
        print(f"  Ví dụ 5 tệp âm thanh đầu:")
        for t in am_thanh[:5]:
            print(f"    · {t}")
        if am_thanh and am_thanh[0].lower().endswith(".sph"):
            print("\n  ℹ Đây là .sph (NIST SPHERE) — KHÔNG phải .wav; soundfile không đọc được.")
            print("    Script tự giải mã bằng bộ đọc SPHERE thuần Python (không cần ffmpeg/sox).")
            print(f"    Dự phòng nếu mã hoá lạ: ffmpeg {'có' if co_lenh('ffmpeg') else 'KHÔNG có'} · "
                  f"sox {'có' if co_lenh('sox') else 'KHÔNG có'}")
        if gioi_han and len(ten) > gioi_han:
            print(f"  … (còn {len(ten) - gioi_han} mục)")


def nap_tar(p: Path, ra_manifest: Path, gioi_han: int = 0, giu_sph: bool = False) -> int:
    print(f"▶ Đọc tar: {p.relative_to(GOC)}  ({p.stat().st_size / 1024 ** 2:.0f} MB)")
    dong: list[dict] = []
    dem_loi = 0
    dem_cach: dict[str, int] = {}
    with tarfile.open(p, "r:gz") as tar:
        ten = tar.getnames()
        # gom prompts + genders theo tập (train / test)
        prompts: dict[str, str] = {}
        genders: dict[str, str] = {}
        for t in ten:
            tl = t.lower()
            if tl.endswith("prompts.txt"):
                prompts.update(doc_prompts(tar, t))
            elif tl.endswith("genders.txt") or tl.endswith("spk2gender"):
                genders.update(doc_genders(tar, t))
        print(f"  Lời thoại: {len(prompts)} câu · Giới tính: {len(genders)} người nói")

        am_thanh = [t for t in ten if t.lower().endswith(DUOI_AM_THANH)]
        if gioi_han:
            am_thanh = am_thanh[:gioi_han]
        print(f"  Cần xử lý: {len(am_thanh)} tệp âm thanh")

        for i, ten_tar in enumerate(am_thanh, 1):
            if i % 1000 == 0:
                print(f"    … {i}/{len(am_thanh)}", flush=True)
            goc_ten = Path(ten_tar)
            spk = goc_ten.parent.name or "khong_ro"
            khoa = goc_ten.stem
            dich = VIVOS / "wav" / spk / f"{khoa}.wav"

            ok = False
            if goc_ten.suffix.lower() == ".wav":
                # đã là wav → bung thẳng
                f = tar.extractfile(ten_tar)
                if f is not None:
                    dich.parent.mkdir(parents=True, exist_ok=True)
                    dich.write_bytes(f.read())
                    ok = True
            else:
                if giu_sph:
                    tam = VIVOS / "sph" / spk / goc_ten.name
                    f = tar.extractfile(ten_tar)
                    if f is not None:
                        tam.parent.mkdir(parents=True, exist_ok=True)
                        tam.write_bytes(f.read())
                        ok, cach = chuyen_sang_wav(tam, dich)
                        dem_cach[cach] = dem_cach.get(cach, 0) + 1
                else:
                    tam = VIVOS / "_tam" / goc_ten.name
                    f = tar.extractfile(ten_tar)
                    if f is not None:
                        tam.parent.mkdir(parents=True, exist_ok=True)
                        tam.write_bytes(f.read())
                        ok, cach = chuyen_sang_wav(tam, dich)
                        dem_cach[cach] = dem_cach.get(cach, 0) + 1
                        tam.unlink(missing_ok=True)
            if not ok:
                dem_loi += 1
                continue
            dong.append({
                "duong_dan": str(dich.relative_to(GOC)),
                "van_ban": prompts.get(khoa, ""),
                "nguon": "vivos", "nguoi_noi": spk,
                "gioi_tinh": genders.get(spk, "khong_ro"),
                "vung_mien": "khong_ro",
            })

    if not dong:
        print("❌ Không chuyển được dòng nào.")
        if dem_loi:
            print(f"   {dem_loi} tệp lỗi — xem lại cảnh báo .sph ở trên (cần ffmpeg hoặc sox).")
        return 1
    df = pd.DataFrame(dong)
    ra_manifest.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(ra_manifest, index=False, encoding="utf-8-sig")
    thieu_text = int((df["van_ban"].astype(str).str.strip() == "").sum())
    print(f"\n✅ {len(df):,} dòng · {df['nguoi_noi'].nunique()} người nói · lỗi {dem_loi}")
    if dem_cach:
        print("   Cách chuyển: " + " · ".join(f"{k}={v}" for k, v in sorted(dem_cach.items())))
    if thieu_text:
        print(f"⚠  {thieu_text} dòng KHÔNG có lời thoại — kiểm lại prompts.txt trong tar")
    print(f"→ {ra_manifest.relative_to(GOC)}")
    print(f"→ {VIVOS.relative_to(GOC)}/wav/")
    return 0


# ══════════════════════════════════════════════════════════════════════
# Đường 2: PARQUET (giữ để tương thích)
# ══════════════════════════════════════════════════════════════════════
def tim_cot(df: pd.DataFrame, ung_vien: list[str]) -> str | None:
    for c in ung_vien:
        if c in df.columns:
            return c
    return None


def giai_ma_audio(o):
    if o is None:
        return None
    if isinstance(o, dict):
        if o.get("bytes") is None and o.get("path") and Path(o["path"]).exists():
            y, sr = sf.read(o["path"], dtype="float32", always_2d=False)
            return np.asarray(y, dtype=np.float32), int(sr)
        if o.get("bytes") is None:
            return None
        return sf.read(io.BytesIO(o["bytes"]), dtype="float32", always_2d=False)
    if isinstance(o, (bytes, bytearray)):
        y, sr = sf.read(io.BytesIO(o), dtype="float32", always_2d=False)
        return np.asarray(y, dtype=np.float32), int(sr)
    if isinstance(o, str) and Path(o).exists():
        y, sr = sf.read(o, dtype="float32", always_2d=False)
        return np.asarray(y, dtype=np.float32), int(sr)
    return None


def nap_parquet(ds_parquet: list[Path], ra_manifest: Path, gioi_han: int = 0) -> int:
    dong: list[dict] = []
    dem = 0
    for p in ds_parquet:
        df = pd.read_parquet(p)
        c_audio = tim_cot(df, ["audio", "wav", "file"])
        c_text = tim_cot(df, ["sentence", "text", "transcript"])
        c_spk = tim_cot(df, ["speaker_id", "client_id", "speaker", "path"])
        if c_audio is None or c_text is None:
            print(f"⚠  Bỏ {p.name}: không nhận ra cột. Có: {list(df.columns)}")
            continue
        for _, r in df.iterrows():
            if gioi_han and dem >= gioi_han:
                break
            ad = giai_ma_audio(r[c_audio])
            if ad is None:
                continue
            y, sr = ad
            if getattr(y, "ndim", 1) > 1:
                y = y.mean(axis=1)
            spk = str(r[c_spk]).split("/")[0].strip() or "khong_ro" if c_spk else "khong_ro"
            ma = f"{p.stem}_{dem:06d}"
            dich = VIVOS / "wav" / spk / f"{ma}.wav"
            dich.parent.mkdir(parents=True, exist_ok=True)
            sf.write(str(dich), np.asarray(y, dtype=np.float32), int(sr), subtype="PCM_16")
            dong.append({"duong_dan": str(dich.relative_to(GOC)),
                         "van_ban": str(r[c_text]).strip(), "nguon": "vivos",
                         "nguoi_noi": spk, "gioi_tinh": "khong_ro", "vung_mien": "khong_ro"})
            dem += 1
        if gioi_han and dem >= gioi_han:
            break
    if not dong:
        print("❌ Không chuyển được dòng nào từ parquet.")
        return 1
    df_tho = pd.DataFrame(dong)
    ra_manifest.parent.mkdir(parents=True, exist_ok=True)
    df_tho.to_csv(ra_manifest, index=False, encoding="utf-8-sig")
    print(f"\n✅ {len(df_tho):,} dòng · {df_tho['nguoi_noi'].nunique()} người nói")
    print(f"→ {ra_manifest.relative_to(GOC)}")
    return 0


# ══════════════════════════════════════════════════════════════════════
def main() -> int:
    ap = argparse.ArgumentParser(description="VIVOS (tar.gz hoặc parquet) → wav + manifest thô")
    ap.add_argument("--goc", default=str(VIVOS), help="thư mục chứa dữ liệu VIVOS")
    ap.add_argument("--tar", default="", help="đường dẫn tệp .tar.gz cụ thể")
    ap.add_argument("--ra", default="data/RAW/_manifest_tho.csv")
    ap.add_argument("--gioi-han", type=int, default=0, help="chỉ xử lý N tệp (để thử)")
    ap.add_argument("--kiem", action="store_true", help="chỉ xem kho có gì, không ghi")
    ap.add_argument("--chi-lap-danh-sach", action="store_true", help="liệt kê thành phần tar")
    ap.add_argument("--giu-sph", action="store_true", help="giữ lại tệp .sph sau khi chuyển")
    a = ap.parse_args()

    goc = Path(a.goc)
    if not goc.is_absolute():
        goc = GOC / goc

    ds_tar = [Path(a.tar)] if a.tar else tim_tar(goc)
    ds_parquet = tim_parquet(goc)

    if not ds_tar and not ds_parquet:
        print(f"❌ Không thấy .tar.gz hoặc .parquet trong {goc}")
        print("   Chạy trước: python tools/du_lieu/tai_du_lieu.py --nguon vivos")
        return 1

    print(f"Kho: {goc.relative_to(GOC) if goc.is_relative_to(GOC) else goc}")
    for p in ds_tar:
        print(f"  · tar     {p.name}  ({p.stat().st_size / 1024 ** 2:.0f} MB)")
    for p in ds_parquet:
        print(f"  · parquet {p.relative_to(goc)}  ({p.stat().st_size / 1024 ** 2:.1f} MB)")

    if a.kiem or a.chi_lap_danh_sach:
        for p in ds_tar:
            print(f"\nNội dung {p.name}:")
            liet_ke_tar(p)
        return 0

    ra = Path(a.ra)
    if not ra.is_absolute():
        ra = GOC / ra

    if ds_tar:
        return nap_tar(ds_tar[0], ra, a.gioi_han, a.giu_sph)
    return nap_parquet(ds_parquet, ra, a.gioi_han)


if __name__ == "__main__":
    raise SystemExit(main())
