#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A3 — Quét chỗ còn tiếng Anh trong dự án (phục vụ yêu cầu "chuyển hết về tiếng Việt").

    python tools/du_lieu/quet_viet_hoa.py
    python tools/du_lieu/quet_viet_hoa.py --chi-tiet
    python tools/du_lieu/quet_viet_hoa.py --nguong 0     # thất bại nếu còn chỗ nào

Chỉ BÁO CÁO, không tự sửa. Mỗi dòng trong data/LOG/viet_hoa_can_sua.csv là một chỗ
cần người/agent xem lại: chuỗi hiển thị cho người dùng, chú thích, hoặc đoạn văn.

Chia kết quả làm 4 vùng:

    A. PHẠM VI PHA A     — phải sửa. CHỈ phần này quyết định cổng G9.
    B. VÙNG CẤM          — ui/, server/, eval/, kaggle/, notebook/, phieu/, qc/, docs/
                           (trừ docs/GHI_CHU_OMNIVOICE.md). Chỉ ĐẾM, không sửa, không tính cổng.
    C. MIỄN TRỪ          — chỗ đã giải trình trong data/LOG/viet_hoa_mien_tru.csv, phải có
                           cột ly_do >= 15 ký tự. Để trống thì vẫn tính là phải sửa.
    D. CHƯA KHAI BÁO     — tệp không thuộc A/B. Phải bổ sung vào 06 §2b.

Mã thoát: 0 nếu số chỗ cần sửa trong phạm vi Pha A ≤ --nguong (mặc định 0).
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
import re
import tokenize
from collections import Counter
from pathlib import Path

GOC = Path(__file__).resolve().parents[2]
BO_QUA = {".git", "data", "node_modules", "dist", "build", "__pycache__", ".venv",
          ".cache", ".local", "out", "target", "coverage", ".agents"}
DUOI = {".py", ".md", ".html", ".txt", ".js", ".css"}

# ── Phân vùng: cổng G9 chỉ tính phần Pha A. Sửa vùng cấm để đạt 0 là gian lận. ──
THU_MUC_PHA_A = ("tools/", "docs/", "data/LOG/")
TEP_PHA_A = {"README.md", "DECISIONS.md", "MO_TA_DU_AN.md",
             "docs/chuc-nang.html", "docs/bao-cao.md", "docs/nguon-du-lieu.md",
             "docs/thay-the-MOS.md", "docs/CAU-TRUC-THU-MUC.md"}
THU_MUC_CAM = ("ui/", "server/", "eval/", "kaggle/", "notebook/", "phieu/", "qc/", "docs/")


def _duong(p: Path) -> str:
    """Đường dẫn tương đối dạng posix (dấu /) — Windows trả '\\' nên phải chuẩn hoá."""
    return p.relative_to(GOC).as_posix()


def vung(tep: str) -> str:
    """'pha_a' | 'cam' | 'khac' — vùng cấm/chưa khai báo không được tính vào cổng G9."""
    if tep in TEP_PHA_A:
        return "pha_a"
    for t in THU_MUC_PHA_A:
        if tep.startswith(t):
            return "pha_a"
    for t in THU_MUC_CAM:
        if tep.startswith(t):
            return "cam"
    return "khac"


def doc_mien_tru(p: Path) -> set[tuple[str, int]]:
    """data/LOG/viet_hoa_mien_tru.csv — mỗi dòng: tep,dong,noi_dung,ly_do.

    Chỗ đã được con người giải trình là KHÔNG cần dịch (tên thư viện, đường dẫn,
    trích dẫn nguyên văn, câu lệnh…) thì đếm riêng, không tính vào số "cần sửa".
    """
    if not p.exists():
        return set()
    import csv
    with p.open(encoding="utf-8-sig", newline="") as f:
        return {(r["tep"].strip(), int(r["dong"])) for r in csv.DictReader(f)
                if r.get("tep") and r.get("dong", "").strip().isdigit()
                and len((r.get("ly_do") or "").strip()) >= 15}

CHU_VIET = set("àáảãạăằắẳẵặâầấẩẫậđèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵ"
               "ÀÁẢÃẠĂẰẮẲẴẶÂẦẤẨẪẬĐÈÉẺẼẸÊỀẾỂỄỆÌÍỈĨỊÒÓỎÕỌÔỒỐỔỖỘƠỜỚỞỠỢÙÚỦŨỤƯỪỨỬỮỰỲÝỶỸỴ")

RE_TU = re.compile(r"[A-Za-z][A-Za-z'\-]+")
RE_TAG = re.compile(r"<[^>]{1,300}>")
RE_KHOI = re.compile(r"<(style|script)\b.*?</\1>", re.S | re.I)

# từ tiếng Anh thường gặp trong mã (không phải câu cho người đọc) — bỏ qua
TU_MA = {"true", "false", "none", "null", "utf", "ascii", "error", "warning",
         "info", "debug", "trace", "get", "post", "put", "delete", "head"}


def co_chu_viet(s: str) -> bool:
    return any(c in CHU_VIET for c in s)


DUOI_TEP = ("py|wav|csv|json|md|html|txt|png|js|css|gz|tar|zip|pt|log|npz|npy|"
            "yaml|yml|toml|cfg|ini|ipynb|docx|xlsx|sh|bat|ps1")


def la_ma(s: str) -> bool:
    """Chuỗi trông giống mã/CSS/đường dẫn/câu lệnh, không phải câu cho người đọc."""
    t = s.strip()
    if any(k in s for k in ("://", "{", "}", "\\", "==", "()", "__", "->", ";", "px ")):
        return True
    if re.fullmatch(r"[\w./\-]+\.(" + DUOI_TEP + r")", t):
        return True
    if re.fullmatch(r"[a-z0-9_|\-]+", t):
        return True
    # đường dẫn thư mục: có dấu / và không có khoảng trắng
    if "/" in t and not re.search(r"\s", t):
        return True
    # câu lệnh trong docstring: "python tools/... --co"
    if re.search(r"(^|\s)(python|py|pip|git|npm)\s+\S*\w\.py\b", t):
        return True
    if re.search(r"(^|\s)--[a-z][a-z\-]+", t):
        return True
    return False


def tu_co_nghia(s: str) -> int:
    """Số từ tiếng Anh 'có nghĩa' (≥3 ký tự, không phải từ khoá mã)."""
    return len([w for w in RE_TU.findall(s) if len(w) >= 3 and w.lower() not in TU_MA])


def quet_py(p: Path) -> list[dict]:
    """Dùng tokenize để lấy đúng chuỗi, không bắt nhầm mã nguồn."""
    ra: list[dict] = []
    try:
        with p.open("rb") as f:
            for tok in tokenize.tokenize(f.readline):
                if tok.type != tokenize.STRING:
                    continue
                s = tok.string
                tien_to = re.match(r"^[rbuf]{0,2}", s, re.I).group(0)
                than = s[len(tien_to):]
                if len(than) >= 2 and than[0] == than[-1] and than[0] in "'\"":
                    than = than[1:-1]
                if len(than) < 12 or co_chu_viet(than) or la_ma(than):
                    continue
                if tu_co_nghia(than) >= 3 and not re.search(r"\n\s{0,8}[A-Za-z_]+ =", than):
                    ra.append({"tep": _duong(p), "dong": tok.start[0],
                               "loai": "chuoi_py", "noi_dung": than.replace("\n", " ")[:200]})
    except (tokenize.TokenError, IndentationError, SyntaxError):
        pass
    return ra


def quet_html(p: Path) -> list[dict]:
    ra: list[dict] = []
    tho = p.read_text(encoding="utf-8", errors="ignore")
    # thay khối <style>/<script> bằng dấu cách nhưng giữ số dòng
    sach = RE_KHOI.sub(lambda m: "\n" * m.group(0).count("\n"), tho)
    for i, dong in enumerate(sach.splitlines(), 1):
        d = RE_TAG.sub(" ", dong)
        d = re.sub(r"\s+", " ", d).strip()
        if len(d) < 25 or co_chu_viet(d) or la_ma(d):
            continue
        if tu_co_nghia(d) >= 6:
            ra.append({"tep": _duong(p), "dong": i, "loai": "giao_dien",
                       "noi_dung": d[:200]})
    return ra


def quet_van_ban(p: Path) -> list[dict]:
    ra: list[dict] = []
    trong_code = False
    for i, dong in enumerate(p.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
        d = dong.strip()
        if d.startswith("```"):
            trong_code = not trong_code
            continue
        if trong_code or not d:
            continue
        # bỏ các đoạn trong dấu `…`: đó là tên tệp / tên biến / câu lệnh, không phải văn xuôi
        d = re.sub(r"`[^`]*`", " ", d)
        d = re.sub(r"\s+", " ", d).strip()
        if len(d) < 25 or co_chu_viet(d):
            continue
        if d.startswith(("#", "|", ">", "-", "*", "!", "//", "<")):
            d = d.lstrip("#<>|>-*! ").strip()
        # trích dẫn tài liệu + câu lệnh cài đặt: giữ nguyên, không dịch
        if re.search(r"\bet al\.|\bdoi\b|https?://|©", d):
            continue
        if re.match(r"^(python|py|pip|winget|brew|sudo|apt|npm|git|curl|cd|ls|cat|set|export)\b", d):
            continue
        if len(d) < 25 or la_ma(d):
            continue
        if tu_co_nghia(d) >= 6:
            ra.append({"tep": _duong(p), "dong": i, "loai": "doan_van",
                       "noi_dung": d[:200]})
    return ra


def main() -> int:
    ap = argparse.ArgumentParser(description="Quét chỗ còn tiếng Anh")
    ap.add_argument("--nguong", type=int, default=0,
                    help="số chỗ tối đa còn chấp nhận được TRONG PHẠM VI PHA A (mặc định 0)")
    ap.add_argument("--chi-tiet", action="store_true", help="in từng dòng")
    ap.add_argument("--json", default="data/LOG/viet_hoa_can_sua.csv")
    ap.add_argument("--mien-tru", default="data/LOG/viet_hoa_mien_tru.csv",
                    help="danh sách chỗ đã giải trình là không cần dịch (tep,dong,noi_dung,ly_do)")
    ap.add_argument("--tinh-ca-vung-cam", action="store_true",
                    help="tính cả vùng cấm vào mã thoát (mặc định KHÔNG — sửa vùng cấm là gian lận)")
    a = ap.parse_args()

    mien_tru = doc_mien_tru(GOC / a.mien_tru)
    ket: list[dict] = []
    da_mien_tru = 0
    for p in sorted(GOC.rglob("*")):
        if not p.is_file() or p.suffix.lower() not in DUOI:
            continue
        phan = p.relative_to(GOC).parts
        if any(x in BO_QUA for x in phan):
            continue
        try:
            if p.suffix == ".py":
                them = quet_py(p)
            elif p.suffix == ".html":
                them = quet_html(p)
            else:
                them = quet_van_ban(p)
        except Exception:
            continue
        for k in them:
            k["vung"] = vung(k["tep"])
            if (k["tep"], k["dong"]) in mien_tru:
                k["vung"] = "mien_tru"
                da_mien_tru += 1
            ket.append(k)

    pha_a = [k for k in ket if k["vung"] == "pha_a"]
    cam = [k for k in ket if k["vung"] == "cam"]
    khac = [k for k in ket if k["vung"] == "khac"]

    def in_bang(tieu_de: str, ds: list[dict]) -> None:
        print("-" * 90)
        print(f"  {tieu_de}: {len(ds)} chỗ")
        dem = Counter(x["tep"] for x in ds)
        for tep, n in dem.most_common():
            print(f"    {n:>4}  {tep}")
        if a.chi_tiet:
            for k in sorted(ds, key=lambda z: (z["tep"], z["dong"])):
                print(f"      [{k['loai']}] {k['tep']}:{k['dong']}  {k['noi_dung']}")

    print("=" * 90)
    print("  QUÉT TIẾNG ANH CÒN SÓT  (cổng G9 chỉ tính phần Pha A)")
    print("=" * 90)
    if not ket:
        print("  ✅ Không tìm thấy chuỗi/đoạn văn tiếng Anh nào.")
    in_bang("A. PHẠM VI PHA A — phải sửa", pha_a)
    in_bang("B. VÙNG CẤM — không được sửa, chỉ ghi số", cam)
    in_bang("C. MIỄN TRỪ — đã giải trình (data/LOG/viet_hoa_mien_tru.csv)", 
            [k for k in ket if k["vung"] == "mien_tru"])
    if khac:
        in_bang("D. CHƯA KHAI BÁO VÙNG — phải bổ sung vào 06 §2b", khac)

    print("-" * 90)
    so_can_sua = len(pha_a) + len(khac)
    print(f"  G9 · cần sửa (Pha A + chưa khai báo): {so_can_sua}   "
          f"ngưỡng {a.nguong} · miễn trừ {da_mien_tru} · vùng cấm {len(cam)}")
    if so_can_sua == 0:
        print("  ✅ QUA CỔNG G9 — phần Pha A không còn tiếng Anh.")
    else:
        print(f"  ❌ CHƯA QUA — còn {so_can_sua} chỗ phải sửa (hoặc phải khai báo miễn trừ kèm lý do).")

    ra = Path(a.json)
    if not ra.is_absolute():
        ra = GOC / ra
    ra.parent.mkdir(parents=True, exist_ok=True)
    import pandas as pd
    pd.DataFrame(ket, columns=["tep", "dong", "loai", "vung", "noi_dung"]).to_csv(
        ra, index=False, encoding="utf-8-sig")
    print(f"  Đã ghi: {ra.relative_to(GOC)}")

    mt = Path(a.mien_tru)
    if not mt.is_absolute():
        mt = GOC / a.mien_tru
    con_lai = pha_a + khac
    if not mt.exists() and con_lai:
        mt.parent.mkdir(parents=True, exist_ok=True)
        import csv as _csv
        with mt.open("w", encoding="utf-8-sig", newline="") as f:
            w = _csv.writer(f)
            w.writerow(["tep", "dong", "noi_dung", "ly_do"])
            for k in sorted(con_lai, key=lambda z: (z["tep"], z["dong"])):
                w.writerow([k["tep"], k["dong"], k["noi_dung"][:120], ""])
        print(f"  ℹ Chưa có tệp miễn trừ → đã tạo bản nháp: {a.mien_tru}")
        print("    Điền cột ly_do (≥ 15 ký tự) cho những chỗ THẬT SỰ không cần dịch.")
        print("    Để trống = vẫn tính là chỗ phải sửa.")

    if a.tinh_ca_vung_cam:
        return 0 if (so_can_sua + len(cam)) <= a.nguong else 1
    return 0 if so_can_sua <= a.nguong else 1


if __name__ == "__main__":
    raise SystemExit(main())
