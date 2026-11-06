#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A1.7b — Soi 7 tệp .pt: bên trong có gì, dùng được cho việc gì, có lấy lại được âm thanh không.

Đây KHÔNG phải script để thay thế việc dùng .pt — .pt là định dạng chính thức của OmniVoice
(`VoiceClonePrompt.save()` / `.load()`). Script này để trả lời 3 câu hỏi khó:

  1. Tệp .pt được ghi bởi phiên bản omnivoice nào, có chứa những trường gì?
  2. Có lấy lại được **âm thanh tham chiếu** từ .pt không (để cắt clip 3/6/10 giây)?
  3. Nếu lấy được, chất lượng còn bao nhiêu?

Chạy trên máy có torch (không cần GPU):
    python tools/du_lieu/kiem_pt.py --thu-muc data/RAW/giong_pt

Chạy trên Kaggle (có GPU + omnivoice) để giải mã ra WAV:
    python tools/du_lieu/kiem_pt.py --thu-muc /kaggle/input/giong --giai-ma data/REF/wav

Mã thoát: 0 = đọc được toàn bộ tệp · 1 = có tệp không đọc được.
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
from pathlib import Path

GOC = Path(__file__).resolve().parents[2]
MA_GIONG = ["U_LINH", "ONG_GIA", "KE", "TRAN_THY", "NU_TRE", "TRAI_TRE", "TRE_EM"]
TAN_SO_MA = 25.0      # OmniVoice: 8 sổ mã âm học ở 25 Hz → 25 khung/giây
TAN_SO_RA = 24000     # âm thanh ra của model


# ── đọc tệp .pt theo 2 đường ────────────────────────────────────────────
def doc_pt(p: Path):
    """Trả về (đối tượng, cách đọc, ghi chú). Không bao giờ ném lỗi ra ngoài."""
    # đường 1 — API chính thức của omnivoice (an toàn nhất, có kiểm phiên bản)
    try:
        from omnivoice import VoiceClonePrompt
        return VoiceClonePrompt.load(str(p)), "VoiceClonePrompt.load()", ""
    except ImportError:
        ghi_chu = "không có gói omnivoice → đọc thô bằng torch"
    except Exception as e:
        ghi_chu = f"VoiceClonePrompt.load() lỗi ({type(e).__name__}) → đọc thô bằng torch"
    # đường 2 — torch.load thô
    try:
        import torch
    except ImportError:
        return None, "không đọc được", "thiếu torch: pip install torch (hoặc chạy trên Kaggle)"
    for w_only in (False, True):
        try:
            return torch.load(str(p), map_location="cpu", weights_only=w_only), \
                   f"torch.load(weights_only={w_only})", ghi_chu
        except Exception:
            continue
    return None, "không đọc được", ghi_chu or "cả 2 chế độ torch.load đều lỗi"


def mo_ta(doi_tuong) -> dict:
    """Mô tả cấu trúc bên trong: trường nào, kiểu gì, kích thước bao nhiêu."""
    thong_tin: dict = {"lop": type(doi_tuong).__name__, "truong": {}}
    nguon = None
    if hasattr(doi_tuong, "__dict__") and doi_tuong.__dict__:
        nguon = doi_tuong.__dict__
    elif isinstance(doi_tuong, dict):
        nguon = doi_tuong
    if nguon is None:
        thong_tin["truong"]["<giá trị>"] = repr(doi_tuong)[:120]
        return thong_tin

    co_ma, so_khung, so_so_ma, co_embed, co_text = False, 0, 0, False, False
    for k, v in nguon.items():
        mo = f"{type(v).__name__}"
        kl = k.lower()
        if hasattr(v, "shape"):
            mo += f" shape={tuple(v.shape)} dtype={getattr(v, 'dtype', '?')}"
            # OmniVoice lưu mã âm học ở trường "ref_audio_tokens" (8 sổ mã × N khung)
            if any(t in kl for t in ("token", "code")) and len(tuple(v.shape)) >= 2:
                co_ma = True
                so_so_ma = int(tuple(v.shape)[0])
                so_khung = int(tuple(v.shape)[-1])
        elif isinstance(v, str):
            mo += f" = {v[:60]!r}"
            if v.strip():
                co_text = True
        elif isinstance(v, (bool, int, float)):
            mo += f" = {v}"
        else:
            mo += f" {repr(v)[:60]}"
        if any(t in kl for t in ("spk", "embed", "x_vector", "speaker")):
            co_embed = True
        thong_tin["truong"][k] = mo

    thong_tin["co_ma_am_hoc"] = co_ma
    thong_tin["so_so_ma"] = so_so_ma
    thong_tin["co_embedding"] = co_embed
    thong_tin["co_ref_text"] = co_text
    if co_ma and so_khung:
        thong_tin["do_dai_uoc_tinh_giay"] = round(so_khung / TAN_SO_MA, 2)
        # .pt chỉ cần ref_audio_tokens + ref_text là đủ để sinh giọng (VoiceClonePrompt tối giản)
        thong_tin["du_de_sinh_giong"] = True
    return thong_tin


# ── giải mã mã âm học → WAV ─────────────────────────────────────────────
def giai_ma(p, doi_tuong, ra: Path) -> tuple[bool, str]:
    """Thử các đường giải mã có thể. Trả về (thành công, giải thích)."""
    try:
        import torch
        from omnivoice import OmniVoice
        import soundfile as sf
    except ImportError as e:
        return False, f"thiếu gói ({e}) — chỉ giải mã được trên Kaggle có GPU"

    try:
        model = OmniVoice.from_pretrained("k2-fsa/OmniVoice", device_map="cuda:0",
                                          dtype=torch.float16, load_asr=False)
    except Exception as e:
        return False, f"không nạp được model ({type(e).__name__})"

    # tìm bộ mã hoá âm thanh và các hàm giải mã có thể có
    tok = None
    for ten in ("audio_tokenizer", "tokenizer", "codec", "audio_codec", "sound_tokenizer"):
        tok = getattr(model, ten, None)
        if tok is not None:
            break
    if tok is None:
        return False, ("không thấy bộ mã hoá âm thanh trong model — "
                       "gửi lại dòng này cho người viết: " + str([a for a in dir(model) if 'tok' in a.lower() or 'code' in a.lower()]))

    ma = None
    nguon = doi_tuong.__dict__ if hasattr(doi_tuong, "__dict__") else (
        doi_tuong if isinstance(doi_tuong, dict) else {})
    for k, v in nguon.items():
        if any(t in k.lower() for t in ("token", "code")) and hasattr(v, "shape"):
            ma = v
            break
    if ma is None:
        return False, "không thấy trường mã âm học trong tệp .pt"

    da_thu = []
    for ten_ham in ("decode", "decode_waveform", "detokenize", "codes_to_wav", "to_wav"):
        f = getattr(tok, ten_ham, None)
        if not callable(f):
            continue
        da_thu.append(ten_ham)
        for bien_the in (ma, ma.unsqueeze(0) if hasattr(ma, "unsqueeze") else ma):
            try:
                y = f(bien_the)
                if isinstance(y, (tuple, list)):
                    y = y[0]
                if hasattr(y, "detach"):
                    y = y.detach().float().cpu().numpy()
                import numpy as np
                y = np.asarray(y, dtype="float32").squeeze()
                if y.ndim == 1 and len(y) > 1000:
                    ra.mkdir(parents=True, exist_ok=True)
                    dich = ra / f"{p.stem}.wav"
                    sf.write(str(dich), y, TAN_SO_RA, subtype="PCM_16")
                    return True, f"{ten_ham}() → {dich} ({len(y) / TAN_SO_RA:.2f} giây)"
            except Exception:
                continue
    return False, ("đã thử " + ", ".join(da_thu) + " nhưng không ra dạng sóng. "
                   "Thuộc tính có trên bộ mã hoá: "
                   + str([a for a in dir(tok) if not a.startswith('_')][:25]))


# ── chương trình chính ──────────────────────────────────────────────────
def main() -> int:
    ap = argparse.ArgumentParser(description="Soi tệp .pt giọng tham chiếu")
    ap.add_argument("--thu-muc", required=True, help="thư mục chứa các tệp .pt")
    ap.add_argument("--giai-ma", default="", help="thư mục ghi WAV giải mã được (cần GPU + omnivoice)")
    ap.add_argument("--json", default="data/LOG/kiem_pt.json", help="nơi ghi báo cáo JSON")
    a = ap.parse_args()

    thu_muc = Path(a.thu_muc)
    if not thu_muc.is_absolute():
        thu_muc = GOC / thu_muc
    ds = sorted(thu_muc.glob("*.pt"))
    if not ds:
        print(f"❌ Không thấy tệp .pt nào trong {thu_muc}")
        return 1

    print("=" * 96)
    print(f"  SOI {len(ds)} TỆP .pt — {thu_muc}")
    print("=" * 96)

    bao_cao, hong = [], 0
    for p in ds:
        print(f"\n▶ {p.name}  ({p.stat().st_size / 1024:.1f} KB)")
        doi_tuong, cach_doc, ghi_chu = doc_pt(p)
        if doi_tuong is None:
            print(f"  ❌ không đọc được — {ghi_chu}")
            bao_cao.append({"tep": p.name, "doc_duoc": False, "loi": ghi_chu})
            hong += 1
            continue
        tt = mo_ta(doi_tuong)
        print(f"  lớp: {tt['lop']} · đọc bằng: {cach_doc}" + (f" · {ghi_chu}" if ghi_chu else ""))
        for k, v in tt["truong"].items():
            print(f"    · {k:<22} {v}")
        print(f"  → có mã âm học: {'có' if tt.get('co_ma_am_hoc') else 'không'}"
              f" · có embedding: {'có' if tt.get('co_embedding') else 'không'}"
              f" · có lời thoại: {'có' if tt.get('co_ref_text') else 'không'}")
        if tt.get("do_dai_uoc_tinh_giay"):
            print(f"  → độ dài âm thanh tham chiếu ước tính: {tt['do_dai_uoc_tinh_giay']} giây")

        muc = {"tep": p.name, "doc_duoc": True, "kich_thuoc_kb": round(p.stat().st_size / 1024, 1),
               "cach_doc": cach_doc, **tt}
        if a.giai_ma and tt.get("co_ma_am_hoc"):
            ok, mo = giai_ma(p, doi_tuong, Path(a.giai_ma))
            muc["giai_ma"] = mo
            print(f"  {'✅' if ok else '⚠'} giải mã: {mo}")
        bao_cao.append(muc)

    # ── tổng kết ──
    doc_duoc = [b for b in bao_cao if b.get("doc_duoc")]
    co_ma = [b for b in doc_duoc if b.get("co_ma_am_hoc")]
    print("\n" + "-" * 96)
    print(f"  Đọc được: {len(doc_duoc)}/{len(bao_cao)} · có mã âm học: {len(co_ma)}/{len(doc_duoc)}")
    if a.giai_ma:
        thanh_cong = [b for b in co_ma if str(b.get("giai_ma", "")).startswith("")]
        print(f"  Giải mã ra WAV: {sum(1 for b in co_ma if 'wav' in str(b.get('giai_ma','')))}/{len(co_ma)}")
    print("-" * 96)
    print("""
  CÁCH ĐỌC KẾT QUẢ
  ─────────────────
  • Tệp .pt là định dạng CHÍNH THỨC của OmniVoice (VoiceClonePrompt.save/load) → dùng được
    cho mọi lần sinh giọng. Giữ nguyên, đừng chuyển đổi.
  • Nếu KHÔNG có mã âm học và KHÔNG có lấy lại được WAV → chỉ mất 2 việc:
      (a) thí nghiệm độ dài clip mẫu 3/6/10 giây (eval/eval_clone.py cần --ref *.wav)
      (b) phát clip gốc cạnh kết quả trong phiếu duyệt
    Khi đó: nêu rõ trong báo cáo là "không làm được thí nghiệm (a) vì chỉ còn .pt".
  • Nếu GIẢI MÃ ĐƯỢC ra WAV → cắt 3/6/10 giây bằng tao_ref.py và dùng bình thường.
    Lưu ý: âm thanh giải mã là BẢN SAO CÓ MẤT MÁT (qua bộ mã hoá), không phải bản thu gốc.
    Ghi rõ điều này trong báo cáo — đừng gọi nó là "bản thu gốc".
""")

    ra = Path(a.json)
    if not ra.is_absolute():
        ra = GOC / ra
    ra.parent.mkdir(parents=True, exist_ok=True)
    ra.write_text(json.dumps({
        "thu_muc": str(thu_muc), "so_tep": len(ds), "doc_duoc": len(doc_duoc),
        "co_ma_am_hoc": len(co_ma), "chi_tiet": bao_cao,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  Đã ghi: {ra.relative_to(GOC) if ra.is_relative_to(GOC) else ra}")
    return 1 if hong else 0


if __name__ == "__main__":
    raise SystemExit(main())
