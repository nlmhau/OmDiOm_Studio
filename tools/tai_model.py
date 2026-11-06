# -*- coding: utf-8 -*-
"""
Script tự động tải trọng số mô hình cho OmDiOm Studio
Hỗ trợ tải model OmniVoice / OmDiOm từ Hugging Face về thư mục cục bộ models/
"""

import os
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

ROOT_DIR = Path(__file__).resolve().parent.parent
MODELS_DIR = ROOT_DIR / "models"
DIR_OMNI = MODELS_DIR / "OmniVoice"
DIR_OMDIOM = MODELS_DIR / "omdiom"

def tai_model():
    print("=" * 65)
    print("  TRÌNH TẢI MÔ HÌNH HỌC SÂU CHO OMDIOM STUDIO")
    print("=" * 65)
    
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    DIR_OMNI.mkdir(parents=True, exist_ok=True)
    DIR_OMDIOM.mkdir(parents=True, exist_ok=True)

    try:
        from huggingface_hub import snapshot_download
    except ImportError:
        print("[!] Chưa cài đặt huggingface_hub. Đang tiến hành cài đặt...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "huggingface_hub"])
        from huggingface_hub import snapshot_download

    print("\n[1/2] Đang tải trọng số mô hình nền tảng 'k2-fsa/OmniVoice' (~2.3 GB)...")
    print("      Quá trình này chỉ chạy một lần duy nhất.")
    try:
        snapshot_download(
            repo_id="k2-fsa/OmniVoice",
            local_dir=str(DIR_OMNI),
            local_dir_use_symlinks=False,
            resume_download=True
        )
        print("  -> Tải thành công OmniVoice vào:", DIR_OMNI)
    except Exception as e:
        print("  -> Lỗi khi tải từ Hugging Face:", e)
        print("  -> Vui lòng kiểm tra lại kết nối Internet.")
        return False

    # Đồng bộ cấu hình sang thư mục omdiom
    print("\n[2/2] Cấu hình môi trường hoạt động cho OmDiOm...")
    st_file = DIR_OMNI / "model.safetensors"
    target_st = DIR_OMDIOM / "model.safetensors"
    if st_file.exists() and not target_st.exists():
        try:
            os.symlink(st_file, target_st)
            print("  -> Đã tạo liên kết model.safetensors sang models/omdiom/")
        except Exception:
            import shutil
            shutil.copy2(st_file, target_st)
            print("  -> Đã sao chép model.safetensors sang models/omdiom/")

    active_file = MODELS_DIR / "active_model.txt"
    if not active_file.exists():
        active_file.write_text("omdiom" if target_st.exists() else "omnivoice", encoding="utf-8")

    print("\n" + "=" * 65)
    print("  HOÀN TẤT CÀI ĐẶT MÔ HÌNH! BÂY GIỜ BẠN CÓ THỂ CHẠY CỤC BỘ.")
    print("  Cách chạy: Click đúp vào file 'chay_local.bat'")
    print("=" * 65)
    return True

if __name__ == "__main__":
    tai_model()

