#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
kiem_goi.py — Cổng kiểm "gói chạy được": UI ↔ notebook ↔ server có khớp nhau.

Vì sao cần: mã máy chủ tồn tại ở HAI nơi —
    · server/*.py            (bản đọc/sửa/chạy thử trên máy)
    · kaggle/OmDiOm.ipynb    (bản nhúng base64, chạy trên Kaggle)
Sửa một bên mà quên bên kia là lỗi rất dễ xảy ra và rất khó thấy: Kaggle chạy
bản cũ, máy bạn chạy bản mới, cùng một giao diện mà hành vi khác nhau.

Dùng:
    python tools/kiem_goi.py            # kiểm, có ✗ là thoát mã 1
    python tools/kiem_goi.py -v         # in thêm chi tiết

Chỉ dùng thư viện chuẩn ⇒ chạy được trên Windows.
"""

from __future__ import annotations

import base64
import hashlib
import json
import re
import sys
from pathlib import Path

GOC = Path(__file__).resolve().parent.parent
UI = GOC / "ui" / "index.html"
NB = GOC / "kaggle" / "OmDiOm.ipynb"
SRV = GOC / "server"
VOICES = GOC / "voices"

CHI_TIET = "-v" in sys.argv


def doc(p: Path) -> str:
    return p.read_text(encoding="utf-8", errors="replace")


def bao(ok: bool, ma: str, ten: str, mo_ta: str) -> bool:
    print(f"  {'✓' if ok else '✗'} {ma}  {ten:34s} {mo_ta}")
    return ok


# ──────────────────────────────────────────────────────────────────── K1 cấu trúc
def k1() -> bool:
    can = {
        "UI/index.html": UI,
        "kaggle/OmDiOm.ipynb": NB,
        "server/app.py": SRV / "app.py",
        "server/engine.py": SRV / "engine.py",
        "server/voices.py": SRV / "voices.py",
        "voices/manifest.json": VOICES / "manifest.json",
    }
    thieu = [k for k, v in can.items() if not v.exists()]
    if thieu:
        return bao(False, "K1", "Đủ tệp", f"thiếu: {', '.join(thieu)}")
    kb = ", ".join(f"{v.name} {v.stat().st_size/1024:.0f} KB" for v in can.values())
    return bao(True, "K1", "Đủ tệp", kb)


# ─────────────────────────────────────────────────────────── K2 UI ↔ endpoint
def endpoints_server() -> set[str]:
    s = doc(SRV / "app.py")
    ds = set()
    for phuong, duong in re.findall(r'@app\.(get|post|delete|put)\("([^"]+)"', s):
        ds.add(duong)
    return ds


def endpoints_ui() -> set[str]:
    """Đường dẫn UI thật sự gọi tới."""
    h = doc(UI)
    ds = set()
    # 1. nối chuỗi: fetch(... + '/health')  →  '/health'
    for x in re.findall(r"""\+\s*'(/[A-Za-z0-9_\-/{}]*)'""", h):
        ds.add(x.rstrip("/") or "/")
    # 2. goiApi('/api/'+tab)  →  mở rộng theo danh sách tab
    if "'/api/'+tab" in h or '"/api/"+tab' in h:
        for t in ("tts", "clone", "design"):
            ds.add(f"/api/{t}")
    # 3. đường dẫn có tham số: '/api/voices/'+id  →  '/api/voices/{id}'
    ds = {re.sub(r"/\+.*$", "", x) for x in ds}
    if any(x.rstrip("/") == "/api/voices" for x in ds):
        ds.add("/api/voices/{voice_id}")
    return {x.rstrip("/") for x in ds if x}


def k2() -> bool:
    srv = {x.rstrip("/") for x in endpoints_server()}
    ui = endpoints_ui()
    thieu = sorted(x for x in ui if x not in srv)
    if CHI_TIET:
        print("       server:", " ".join(sorted(srv)))
        print("       UI gọi:", " ".join(sorted(ui)))
    if thieu:
        return bao(False, "K2", "UI gọi đúng endpoint", f"server không có: {', '.join(thieu)}")
    return bao(True, "K2", "UI gọi đúng endpoint", f"{len(ui)} đường dẫn, đều có trong server")


# ──────────────────────────────────────────── K3 phần tử HTML mà JS bám vào
ID_BAT_BUOC = [
    "knUrl", "knKey", "knTest", "knSave", "knClear", "knOut",
    "selGiongTts", "statusText", "badgeMode", "toast",
]
THUOC_TINH_BAT_BUOC = [
    "data-vlist", "data-vfile", "data-vdrop", "data-vdir", "data-vinfo",
    "data-si", "data-hist", "data-m", "data-run", "data-text",
]


def k3() -> bool:
    h = doc(UI)
    thieu = [f"#{i}" for i in ID_BAT_BUOC if f'id="{i}"' not in h]
    thieu += [a for a in THUOC_TINH_BAT_BUOC if a not in h]
    if thieu:
        return bao(False, "K3", "Đủ phần tử giao diện", f"thiếu: {', '.join(thieu)}")
    return bao(True, "K3", "Đủ phần tử giao diện",
               f"{len(ID_BAT_BUOC)} id + {len(THUOC_TINH_BAT_BUOC)} thuộc tính")


# ────────────────────────────────────────── K4 UI ↔ notebook: bản mã có khớp
def nb_nhung() -> dict[str, bytes]:
    """Giải base64 trong notebook → {tên tệp: nội dung}."""
    raw = json.loads(doc(NB))
    src = "\n".join("".join(c.get("source", []))
                    for c in raw["cells"] if c.get("cell_type") == "code")
    ra = {}
    for ten, b64 in re.findall(r'([A-Za-z_]+)_B64\s*=\s*"([A-Za-z0-9+/=]+)"', src):
        ten_tf = {"APP": "app.py", "ENG": "engine.py", "VOI": "voices.py"}.get(ten)
        if ten_tf:
            ra[ten_tf] = base64.b64decode(b64)
    return ra


def k4() -> bool:
    nhung = nb_nhung()
    if not nhung:
        return bao(False, "K4", "Notebook ↔ server khớp", "không tìm thấy mã nhúng trong notebook")
    lech = []
    for ten, data in nhung.items():
        f = SRV / ten
        if not f.exists():
            lech.append(f"{ten} (thiếu trong server/)")
            continue
        a = hashlib.sha256(data).hexdigest()
        b = hashlib.sha256(f.read_bytes()).hexdigest()
        if a != b:
            lech.append(f"{ten} (notebook {a[:8]} ≠ server {b[:8]})")
        elif CHI_TIET:
            print(f"       {ten:12s} sha256={a[:16]}… khớp")
    if lech:
        return bao(False, "K4", "Notebook ↔ server khớp", "lệch: " + "; ".join(lech))
    return bao(True, "K4", "Notebook ↔ server khớp", f"{len(nhung)} tệp nhúng, sha256 trùng")


# ──────────────────────────────────── K5 notebook có đủ thứ để chạy trên Kaggle
def k5() -> bool:
    raw = json.loads(doc(NB))
    src = "\n".join("".join(c.get("source", []))
                    for c in raw["cells"] if c.get("cell_type") == "code")
    # mã server nằm trong base64 ⇒ phải giải mã rồi mới tìm được
    for data in nb_nhung().values():
        src += "\n" + data.decode("utf-8", errors="replace")
    can = {
        "nvidiaTeslaT4x2": "accelerator T4×2",
        "OMNIVOICE_VOICES": "trỏ thư mục giọng",
        "/kaggle/working/voices": "tạo thư mục giọng",
        "/kaggle/input": "chép .pt từ Dataset",
        "cloudflared": "mở tunnel",
        "voice_id": "mã server có chọn giọng",
    }
    thieu = [v for k, v in can.items() if k not in src
             and k not in raw.get("metadata", {}).get("kaggle", {}).values()]
    acc = raw.get("metadata", {}).get("kaggle", {}).get("accelerator")
    ok = (not thieu) and acc == "nvidiaTeslaT4x2"
    mo = f"{len(raw['cells'])} ô · accelerator={acc}" if ok else f"thiếu: {', '.join(thieu)}"
    return bao(ok, "K5", "Notebook chạy được trên Kaggle", mo)


# ──────────────────────────────────────────────────────────── K6 thư viện giọng
def k6() -> bool:
    man = VOICES / "manifest.json"
    try:
        obj = json.loads(doc(man))
        assert isinstance(obj.get("voices"), list)
    except Exception as e:
        return bao(False, "K6", "Thư viện giọng", f"manifest.json hỏng: {e}")
    pt = sorted(VOICES.glob("*.pt"))
    if not pt:
        return bao(True, "K6", "Thư viện giọng",
                   "manifest hợp lệ · chưa có .pt (chép 7 tệp vào voices/ là xong)")
    tong = sum(p.stat().st_size for p in pt)
    ten = ", ".join(p.stem for p in pt[:4]) + ("…" if len(pt) > 4 else "")
    return bao(True, "K6", "Thư viện giọng", f"{len(pt)} tệp · {tong/1024:.0f} KB · {ten}")


# ────────────────────────────────────────────────── K7 giao diện gửi API key
def k7() -> bool:
    h = doc(UI)
    co = "X-API-Key" in h
    return bao(co, "K7", "Giao diện gửi X-API-Key", "có" if co else "KHÔNG — sẽ bị 401")


PHEP = [
    ("K1", "Đủ tệp", k1),
    ("K2", "UI gọi đúng endpoint", k2),
    ("K3", "Đủ phần tử giao diện", k3),
    ("K4", "Notebook ↔ server khớp", k4),
    ("K5", "Notebook chạy được trên Kaggle", k5),
    ("K6", "Thư viện giọng", k6),
    ("K7", "Giao diện gửi X-API-Key", k7),
]


def main() -> int:
    print(f"Gói: {GOC}\n")
    hong = 0
    for _, _, fn in PHEP:
        try:
            if not fn():
                hong += 1
        except Exception as e:
            print(f"  ✗ lỗi khi kiểm: {type(e).__name__}: {e}")
            hong += 1
    print()
    if hong:
        print(f"❌ {hong}/{len(PHEP)} hỏng.")
        print("   Lệch K4 thường do: sửa server/*.py mà chưa chạy lại bộ sinh notebook.")
        return 1
    print(f"✅ ĐẠT {len(PHEP)}/{len(PHEP)} — gói khớp và chạy được.")
    return 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    sys.exit(main())
