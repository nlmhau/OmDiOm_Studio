#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cau_truc.py — Cổng kiểm cấu trúc thư mục (C1–C7).

Dùng:
    python tools/cau_truc.py            # kiểm, in bảng. Có ✗ → thoát mã 1
    python tools/cau_truc.py tao        # tạo phần còn thiếu (không xoá gì)

Chỉ dùng thư viện chuẩn + đường dẫn pathlib ⇒ chạy được trên Windows/PowerShell
mà không cần lệnh Unix.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

GOC = Path(__file__).resolve().parent.parent

# Tệp được phép nằm lẻ ở gốc.
#   · 5 tệp chuẩn của mọi dự án
#   · 2 tài liệu điều hành: DECISIONS.md (lý do các quyết định), MO_TA_DU_AN.md
CHO_PHEP_O_GOC = {
    "README.md", "requirements.txt", ".gitignore",
    "chay_local.bat",            # một cú nhấp để chạy thử, phải ở gốc mới tiện
    "DECISIONS.md", "MO_TA_DU_AN.md",
}

# Thư mục bỏ qua khi quét
BO_QUA = {".git", "__pycache__", ".venv", "venv", "node_modules", ".ipynb_checkpoints"}

# Đuôi tệp không được nằm cạnh mã nguồn
DUOI_DU_LIEU = {".wav", ".mp3", ".flac", ".m4a", ".pt", ".safetensors", ".bin"}


def _fmt(b: int) -> str:
    return f"{b / 1024:.0f} KB" if b < 1024 * 1024 else f"{b / 2**20:.1f} MB"


def duyet(p: Path):
    """Duyệt đệ quy, bỏ qua thư mục rác."""
    for x in sorted(p.iterdir()):
        if x.name in BO_QUA:
            continue
        yield x
        if x.is_dir():
            yield from duyet(x)


# ─────────────────────────────────────────────────────────────── từng phép kiểm
def c1_tep_le_o_goc() -> tuple[bool, str]:
    la = sorted(p.name for p in GOC.iterdir() if p.is_file())
    la = [x for x in la if not x.startswith(".") or x in CHO_PHEP_O_GOC]
    thua = [x for x in la if x not in CHO_PHEP_O_GOC]
    if thua:
        return False, f"tệp lẻ không được phép: {', '.join(thua)}"
    return True, f"{len(la)} tệp ở gốc — đều nằm trong danh sách điều hướng"


def c2_tep_bat_buoc() -> tuple[bool, str]:
    thieu = [t for t in ("requirements.txt", ".gitignore", "README.md")
             if not (GOC / t).exists()]
    if thieu:
        return False, f"thiếu: {', '.join(thieu)}"
    return True, "có requirements.txt · .gitignore · README.md"


def c3_thu_vien_giong() -> tuple[bool, str]:
    d = GOC / "voices"
    if not d.is_dir():
        return False, "không có thư mục voices/"
    thieu = [t for t in ("README.md", "manifest.json") if not (d / t).exists()]
    if thieu:
        return False, f"voices/ thiếu: {', '.join(thieu)}"
    try:
        obj = json.loads((d / "manifest.json").read_text(encoding="utf-8"))
        if not isinstance(obj.get("voices"), list):
            return False, "manifest.json thiếu khoá 'voices' (mảng)"
    except Exception as e:
        return False, f"manifest.json không đọc được: {e}"
    n_pt = len(list(d.glob("*.pt")))
    n_man = len(obj["voices"])
    if n_pt == 0:
        return True, "voices/ sẵn sàng, chưa có tệp .pt nào (thả 7 tệp vào là xong)"
    return True, f"{n_pt} tệp .pt · manifest ghi {n_man} mục"


def c4_pt_ngoai_thu_vien() -> tuple[bool, str]:
    thua = [str(p.relative_to(GOC)) for p in duyet(GOC)
            if p.is_file() and p.suffix.lower() == ".pt" and p.parent != GOC / "voices"]
    if thua:
        return False, f".pt nằm ngoài voices/: {', '.join(thua[:5])}"
    return True, "mọi .pt đều nằm trong voices/"


def c5_rac() -> tuple[bool, str]:
    rac = []
    for p in duyet(GOC):
        if p.name == "__pycache__" or p.suffix in (".pyc", ".pyo") or p.suffix == ".log":
            rac.append(str(p.relative_to(GOC)))
    if rac:
        return False, f"{len(rac)} tệp rác, vd: {', '.join(rac[:3])}"
    return True, "không có __pycache__ / .pyc / .log"


def c6_ten_khong_dau() -> tuple[bool, str]:
    xau = []
    for p in duyet(GOC):
        if p.is_file() and p.parent == GOC / "voices" and p.suffix == ".pt":
            continue                      # tệp giọng cố ý giữ dấu
        ten = p.name
        if any(ord(c) > 127 for c in ten) or " " in ten:
            xau.append(str(p.relative_to(GOC)))
    if xau:
        return False, f"{len(xau)} tệp có dấu hoặc khoảng trắng: {', '.join(xau[:3])}"
    return True, "tên tệp đều không dấu, không khoảng trắng"


def c7_du_lieu_canh_ma() -> tuple[bool, str]:
    xau = []
    for thu in ("server", "ui", "tools"):
        d = GOC / thu
        if not d.is_dir():
            continue
        for p in duyet(d):
            if p.is_file() and p.suffix.lower() in DUOI_DU_LIEU:
                xau.append(str(p.relative_to(GOC)))
    if xau:
        return False, f"dữ liệu nằm cạnh mã: {', '.join(xau[:3])}"
    return True, "không có .wav/.pt/.bin trong server/ ui/ tools/"


PHEP_KIEM = [
    ("C1", "Tệp lẻ ở gốc", c1_tep_le_o_goc),
    ("C2", "Tệp bắt buộc", c2_tep_bat_buoc),
    ("C3", "Thư viện giọng", c3_thu_vien_giong),
    ("C4", ".pt đúng chỗ", c4_pt_ngoai_thu_vien),
    ("C5", "Không có rác", c5_rac),
    ("C6", "Tên tệp hợp lệ", c6_ten_khong_dau),
    ("C7", "Dữ liệu tách khỏi mã", c7_du_lieu_canh_ma),
]


# ─────────────────────────────────────────────────────────────────── chế độ tạo
def tao() -> int:
    """Tạo phần còn thiếu. Không xoá, không di chuyển gì."""
    da_tao = []

    for ten, noi_dung in [
        ("requirements.txt",
         "omnivoice==0.2.1\nfastapi>=0.110\nuvicorn[standard]>=0.27\n"
         "python-multipart>=0.0.9\nsoundfile>=0.12\nlibrosa>=0.10\n"
         "huggingface_hub>=0.23\nnumpy>=1.24\n"),
        (".gitignore",
         "voices/*.pt\nvoices/*.part\n__pycache__/\n*.py[cod]\n.venv/\nvenv/\n"
         "models/\n*.log\n.ipynb_checkpoints/\n"),
    ]:
        f = GOC / ten
        if not f.exists():
            f.write_text(noi_dung, encoding="utf-8")
            da_tao.append(ten)

    d = GOC / "voices"
    d.mkdir(exist_ok=True)
    man = d / "manifest.json"
    if not man.exists():
        man.write_text('{\n  "voices": []\n}', encoding="utf-8")
        da_tao.append("voices/manifest.json")
    rd = d / "README.md"
    if not rd.exists():
        rd.write_text("# voices/\n\nThư viện giọng đã nhân bản (.pt). Xem docs/CAU-TRUC-THU-MUC.md\n",
                      encoding="utf-8")
        da_tao.append("voices/README.md")

    # dọn rác (an toàn: chỉ __pycache__ và .pyc)
    for p in list(duyet(GOC)):
        if p.is_dir() and p.name == "__pycache__":
            for f in p.glob("*"):
                f.unlink()
            p.rmdir()
            da_tao.append(f"xoá {p.relative_to(GOC)}/")

    print("Đã tạo/sửa:" if da_tao else "Không thiếu gì.")
    for x in da_tao:
        print("  ·", x)
    return 0


# ─────────────────────────────────────────────────────────────────── chế độ kiểm
def kiem() -> int:
    print(f"Thư mục gốc: {GOC}\n")
    hong = 0
    for ma, ten, fn in PHEP_KIEM:
        try:
            ok, mo_ta = fn()
        except Exception as e:                       # không để cổng tự chết
            ok, mo_ta = False, f"lỗi khi kiểm: {type(e).__name__}: {e}"
        print(f"  {'✓' if ok else '✗'} {ma}  {ten:26s} {mo_ta}")
        if not ok:
            hong += 1

    print()
    if hong:
        print(f"❌ {hong}/{len(PHEP_KIEM)} phép kiểm hỏng. Chạy: python tools/cau_truc.py tao")
        return 1
    print(f"✅ ĐẠT {len(PHEP_KIEM)}/{len(PHEP_KIEM)} — cấu trúc thư mục hợp lệ.")
    return 0


def cay() -> None:
    """In cây thư mục gọn (bỏ rác)."""
    print(f"\n{GOC.name}/")

    def _in(p: Path, truoc: str = "") -> None:
        ds = [x for x in sorted(p.iterdir()) if x.name not in BO_QUA]
        for i, x in enumerate(ds):
            cuoi = i == len(ds) - 1
            print(f"{truoc}{'└─ ' if cuoi else '├─ '}{x.name}{'/' if x.is_dir() else ''}")
            if x.is_dir():
                _in(x, truoc + ("   " if cuoi else "│  "))

    _in(GOC)


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")     # PowerShell hiển thị đúng tiếng Việt
    except Exception:
        pass

    os.chdir(GOC)
    if len(sys.argv) > 1 and sys.argv[1] == "tao":
        tao()
        print()
        kiem()
    elif len(sys.argv) > 1 and sys.argv[1] == "cay":
        cay()
    else:
        sys.exit(kiem())
