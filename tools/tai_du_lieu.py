#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A1.3 — Tải dữ liệu nguồn về data/RAW (KHÔNG BAO GIỜ sửa dữ liệu thô).

Ví dụ:
    python tools/du_lieu/tai_du_lieu.py --liet-ke
    python tools/du_lieu/tai_du_lieu.py --nguon omnivoice-code
    python tools/du_lieu/tai_du_lieu.py --tang 0
    python tools/du_lieu/tai_du_lieu.py --tang 1 --kiem     # chỉ in lệnh, không tải

Nguyên tắc:
  • tải xong ghi "giấy khai sinh" của nguồn vào data/RAW/_nguon/<id>.json
    (URL, phiên bản/commit, giấy phép, số tệp, dung lượng, thời điểm)
  • không ghi đè thư mục đã có; muốn tải lại phải xoá tay
  • kiểm dung lượng trống trước khi tải; thiếu thì dừng, không tải dở
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
import os
import shutil
import subprocess
import sys
import urllib.request
from datetime import datetime
from pathlib import Path

GOC = Path(__file__).resolve().parents[2]
RAW = GOC / "data" / "RAW"
SO_NGUON = RAW / "_nguon"
LOG = GOC / "data" / "LOG"

# ══════════════════════════════════════════════════════════════════════
# DANH MỤC NGUỒN — mọi thông tin giấy phép ở đây lấy từ trang gốc, xem docs/nguon-du-lieu.md
# tang 0 = bắt buộc (≈30 phút) · tang 1 = nên có (≈2–3 giờ) · tang 2 = tuỳ chọn
# ══════════════════════════════════════════════════════════════════════
NGUON: dict[str, dict] = {
    "omnivoice-code": {
        "ten": "Mã nguồn k2-fsa/OmniVoice",
        "loai": "git",
        "url": "https://github.com/k2-fsa/OmniVoice.git",
        "dich": "omnivoice",
        "giay_phep": "Apache-2.0 (phần mã); audio_tokenizer dùng giấy phép Boson Higgs Audio 2 Community — xem 02_NGUON_DU_LIEU.md §Giấy phép",
        "tang": 0, "uoc_luong": 0.2,
        "ghi_chu": "Đọc docs/ + omnivoice/ để biết API; KHÔNG sửa gì trong thư mục này.",
    },
    "thu-muc-nguon": {
        "ten": "Danh mục dữ liệu tiếng Việt (awesome list)",
        "loai": "git",
        "url": "https://github.com/lienlt10/awesome-vietnamese-speech-datasets.git",
        "dich": "thu_muc_nguon",
        "giay_phep": "CC0-1.0 (chỉ danh mục, không phải dữ liệu)",
        "tang": 0, "uoc_luong": 0.05,
        "ghi_chu": "Để tra thêm nguồn khi cần; không phải dữ liệu huấn luyện.",
    },
    "vivos": {
        "ten": "VIVOS — 15 giờ, 65 người nói, 16 kHz",
        "loai": "hf",
        "url": "AILAB-VNUHCM/vivos",
        "dich": "vivos",
        "giay_phep": "CC BY-NC-SA 4.0 — chỉ nghiên cứu, phi thương mại, chia sẻ tương tự",
        "tang": 0, "uoc_luong": 1.8,
        "sha256": "", "md5": "72972a8b14050f3f11ea7c3debabd7af",
        "ghi_chu": "Bản tar.gz bố cục Kaldi: data/vivos.tar.gz (1,4 GB) + data/prompts-train.txt.gz "
                   "+ data/prompts-test.txt.gz. Audio trong tar là .sph (NIST SPHERE) — "
                   "nap_vivos.py tự giải mã, không cần ffmpeg/sox. KHÔNG có parquet.",
    },
    "vivos-goc": {
        "ten": "VIVOS bản gốc của AILAB (tar.gz, .sph)",
        "loai": "url",
        "url": "https://zenodo.org/records/7068130/files/vivos.tar.gz",
        "dich": "_tai_ve/vivos.tar.gz",
        "sha256": "", "md5": "72972a8b14050f3f11ea7c3debabd7af",
        "giay_phep": "CC BY-NC-SA 4.0",
        "tang": 2, "uoc_luong": 1.5,
        "ghi_chu": "Chỉ dùng khi đường HF hỏng. .sph của Kaldi → nap_vivos.py giải mã thuần Python.",
    },
    "common-voice-vi": {
        "ten": "Mozilla Common Voice — tiếng Việt (CC0)",
        "loai": "hf",
        "url": "mozilla-foundation/common_voice_17_0",
        "mau": ["vi/*"],
        "dich": "common_voice_vi",
        "giay_phep": "CC0-1.0 — dùng thương mại được (nguồn duy nhất trong danh mục này)",
        "tang": 1, "uoc_luong": 3.0, "can_dang_nhap": True,
        "ghi_chu": "Bắt buộc: đăng nhập HF + bấm đồng ý điều khoản trên trang dataset. "
                   "Chất lượng thu âm không đều → sẽ bị lọc mạnh.",
    },
    "phoaudiobook": {
        "ten": "PhoAudiobook — 941 giờ, 735 người đọc (Movian AI)",
        "loai": "hf",
        "url": "thivux/phoaudiobook",
        "dich": "phoaudiobook",
        "giay_phep": "Nghiên cứu / phi thương mại (theo trang dataset gốc)",
        "tang": 2, "uoc_luong": 60.0,
        "ghi_chu": "RẤT LỚN (~1 triệu dòng). Không tải hết: lấy mẫu theo người nói, "
                   "xem tools/lam_sach.py §Lấy mẫu. Chỉ dùng khi cần chất giọng đa dạng.",
    },
    "vieneu-1000h": {
        "ten": "VieNeu-TTS-1000h",
        "loai": "hf",
        "url": "pnnbao-ump/VieNeu-TTS-1000h",
        "dich": "vieneu_1000h",
        "giay_phep": "CC BY-NC 4.0 — nghiên cứu / giáo dục",
        "tang": 2, "uoc_luong": 100.0,
        "ghi_chu": "Thay thế viVoice nếu bản viVoice bị chặn (cần gửi thông tin liên hệ).",
    },
}


# ── tiện ích ───────────────────────────────────────────────────────────
def ghi_log(dong: str) -> None:
    LOG.mkdir(parents=True, exist_ok=True)
    with (LOG / "tai_du_lieu.log").open("a", encoding="utf-8") as f:
        f.write(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] {dong}\n")


def trong_con_lai_gb(p: Path) -> float:
    p.mkdir(parents=True, exist_ok=True)
    return shutil.disk_usage(str(p)).free / 1024 ** 3


def dem_tep(p: Path) -> tuple[int, int]:
    so, byte = 0, 0
    for r, _, fs in os.walk(p):
        for f in fs:
            so += 1
            try:
                byte += (Path(r) / f).stat().st_size
            except OSError:
                pass
    return so, byte


def ghi_giay_khai_sinh(ma: str, mc: dict, duong_dan: Path, phien_ban: str, ghi_chu: str = "") -> None:
    SO_NGUON.mkdir(parents=True, exist_ok=True)
    so_tep, so_byte = dem_tep(duong_dan) if duong_dan.is_dir() else (1, duong_dan.stat().st_size if duong_dan.exists() else 0)
    ban_ghi = {
        "ma_nguon": ma,
        "ten": mc["ten"],
        "url": mc["url"],
        "phien_ban": phien_ban,
        "giay_phep": mc["giay_phep"],
        "tang": mc["tang"],
        "duong_dan": str(duong_dan.relative_to(GOC)),
        "so_tep": so_tep,
        "dung_luong_mb": round(so_byte / 1024 ** 2, 1),
        "thoi_diem": datetime.now().isoformat(timespec="seconds"),
        "ghi_chu": mc.get("ghi_chu", "") + (f" {ghi_chu}" if ghi_chu else ""),
    }
    ra = SO_NGUON / f"{ma}.json"
    ra.write_text(json.dumps(ban_ghi, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"    ↳ giấy khai sinh: {ra.relative_to(GOC)}  ({so_tep} tệp, {ban_ghi['dung_luong_mb']} MB)")
    ghi_log(f"XONG {ma} · {phien_ban} · {so_tep} tệp · {ban_ghi['dung_luong_mb']} MB")


def tai_git(ma: str, mc: dict) -> int:
    dich = RAW / mc["dich"]
    if dich.exists():
        print(f"  ⏭  {ma}: đã có {dich.relative_to(GOC)} — bỏ qua (không ghi đè)")
        return 0
    print(f"  ⬇  {ma}: git clone --depth 1 → {dich.relative_to(GOC)}")
    r = subprocess.run(["git", "clone", "--depth", "1", mc["url"], str(dich)],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode != 0:
        print(f"  ❌ {ma}: clone lỗi\n{r.stderr.strip()[:400]}")
        ghi_log(f"LOI {ma}: {r.stderr.strip()[:200]}")
        return 1
    commit = subprocess.run(["git", "-C", str(dich), "rev-parse", "HEAD"],
                            capture_output=True, text=True,
                            encoding="utf-8", errors="replace").stdout.strip()
    ghi_giay_khai_sinh(ma, mc, dich, commit[:12])
    return 0


def tai_hf(ma: str, mc: dict) -> int:
    try:
        from huggingface_hub import snapshot_download
    except ImportError:
        print(f"  ❌ {ma}: thiếu huggingface_hub → pip install huggingface_hub")
        return 1
    dich = RAW / mc["dich"]
    if dich.exists() and any(dich.iterdir()):
        print(f"  ⏭  {ma}: đã có {dich.relative_to(GOC)} — bỏ qua")
        return 0
    print(f"  ⬇  {ma}: snapshot_download({mc['url']}) → {dich.relative_to(GOC)}")
    if mc.get("can_dang_nhap"):
        print("     ⚠  bộ dữ liệu này YÊU CẦU đăng nhập HF + đồng ý điều khoản trên web.")
        print("        chạy: hf auth login   (hoặc đặt biến môi trường HF_TOKEN)")
    try:
        duong = snapshot_download(repo_id=mc["url"], repo_type="dataset",
                                  local_dir=str(dich),
                                  allow_patterns=mc.get("mau") or None,
                                  max_workers=4)
    except Exception as e:
        print(f"  ❌ {ma}: {type(e).__name__}: {str(e)[:300]}")
        ghi_log(f"LOI {ma}: {type(e).__name__}")
        return 1
    phien_ban = ""
    try:
        from huggingface_hub import dataset_info
        phien_ban = dataset_info(mc["url"]).sha or ""
    except Exception:
        pass
    ghi_giay_khai_sinh(ma, mc, Path(duong), phien_ban[:12] or "không rõ")
    return 0


def tai_url(ma: str, mc: dict) -> int:
    dich = RAW / mc["dich"]
    dich.parent.mkdir(parents=True, exist_ok=True)
    if dich.exists():
        print(f"  ⏭  {ma}: đã có {dich.relative_to(GOC)} — bỏ qua")
        return 0
    print(f"  ⬇  {ma}: {mc['url']}")
    tam = dich.with_suffix(dich.suffix + ".part")
    h = hashlib.sha256()
    try:
        with urllib.request.urlopen(mc["url"], timeout=120) as r, tam.open("wb") as f:
            tong, da = int(r.headers.get("Content-Length") or 0), 0
            while True:
                khoi = r.read(1 << 20)
                if not khoi:
                    break
                f.write(khoi)
                h.update(khoi)
                da += len(khoi)
                if tong and da % (50 << 20) < (1 << 20):
                    print(f"     … {da / 1024 ** 2:.0f}/{tong / 1024 ** 2:.0f} MB", flush=True)
    except Exception as e:
        print(f"  ❌ {ma}: {type(e).__name__}: {str(e)[:300]}")
        if tam.exists():
            tam.unlink()
        ghi_log(f"LOI {ma}: {type(e).__name__}")
        return 1
    if mc.get("sha256") and h.hexdigest() != mc["sha256"]:
        print(f"  ❌ {ma}: sha256 không khớp — XOÁ tệp, không dùng")
        tam.unlink()
        return 1
    tam.rename(dich)
    ghi_giay_khai_sinh(ma, mc, dich, "sha256:" + h.hexdigest()[:16])
    return 0


def in_liet_ke() -> None:
    print(f"{'mã':<18}{'tầng':<6}{'GB':>6}  {'loại':<5} giấy phép")
    print("-" * 100)
    for ma, mc in NGUON.items():
        print(f"{ma:<18}{mc['tang']:<6}{mc['uoc_luong']:>6.1f}  {mc['loai']:<5} {mc['giay_phep'][:60]}")
    print("-" * 100)
    t = {k: sum(m['uoc_luong'] for m in NGUON.values() if m['tang'] == k) for k in (0, 1, 2)}
    print(f"Ước lượng: tầng 0 = {t[0]:.1f} GB · tầng 1 = {t[1]:.1f} GB · tầng 2 = {t[2]:.1f} GB")


def main() -> int:
    ap = argparse.ArgumentParser(description="Tải dữ liệu nguồn về data/RAW")
    ap.add_argument("--liet-ke", action="store_true", help="in danh mục nguồn")
    ap.add_argument("--nguon", nargs="*", default=[], help="mã nguồn cụ thể")
    ap.add_argument("--tang", type=int, choices=[0, 1, 2], help="tải cả một tầng")
    ap.add_argument("--kiem", action="store_true", help="chỉ in việc sẽ làm, không tải")
    a = ap.parse_args()

    if a.liet_ke:
        in_liet_ke()
        return 0

    chon: list[str] = []
    if a.nguon:
        for ma in a.nguon:
            if ma not in NGUON:
                print(f"❌ Không có mã nguồn '{ma}'. Xem: --liet-ke")
                return 1
            chon.append(ma)
    if a.tang is not None:
        chon += [ma for ma, mc in NGUON.items() if mc["tang"] == a.tang]
    if not chon:
        print("Chưa chọn nguồn nào. Dùng --nguon <mã> hoặc --tang 0|1|2. Xem --liet-ke")
        return 1
    chon = list(dict.fromkeys(chon))

    can = sum(NGUON[m]["uoc_luong"] for m in chon) * 1.2
    trong = trong_con_lai_gb(RAW)
    print(f"Cần ~{can:.1f} GB · còn trống {trong:.1f} GB tại {RAW.relative_to(GOC)}")
    if trong < can:
        print("❌ Không đủ dung lượng — dừng trước khi tải dở.")
        return 1

    print(f"\nSẽ tải {len(chon)} nguồn: {', '.join(chon)}\n")
    if a.kiem:
        for ma in chon:
            mc = NGUON[ma]
            print(f"  · {ma:<18} {mc['loai']:<5} {mc['url']}")
        print("\n(--kiem: chưa tải gì cả)")
        return 0

    RAW.mkdir(parents=True, exist_ok=True)
    loi = 0
    for ma in chon:
        mc = NGUON[ma]
        print(f"\n▶ {ma} — {mc['ten']}")
        if mc["loai"] == "git":
            loi += tai_git(ma, mc)
        elif mc["loai"] == "hf":
            loi += tai_hf(ma, mc)
        elif mc["loai"] == "url":
            loi += tai_url(ma, mc)
        else:
            print(f"  ❌ loại không hỗ trợ: {mc['loai']}")
            loi += 1

    print("-" * 60)
    print(f"XONG: {len(chon) - loi}/{len(chon)} nguồn · lỗi: {loi}")
    if loi:
        print("Đọc docs/CAU-TRUC-THU-MUC.md §6 và MO_TA_DU_AN.md trước khi thử lại.")
    return 1 if loi else 0


if __name__ == "__main__":
    raise SystemExit(main())
