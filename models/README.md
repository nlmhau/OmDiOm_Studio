# 🧠 Hướng Dẫn Quản Lý & Tải Trọng Số Mô Hình (Model Weights)

Thư mục `models/` lưu trữ cấu hình kiến trúc và các tệp trọng số nơ-ron (Neural Network Checkpoints) của hệ thống **OmDiOm Studio**.

---

## 📌 Vì Sao Trọng Số `.safetensors` Không Lưu Trực Tiếp Trên Git?

Tệp trọng số học sâu `model.safetensors` của mô hình có dung lượng **~2.33 GB** (kèm bộ mã hóa âm thanh `audio_tokenizer/model.safetensors` **~768 MB**). Theo quy định kỹ thuật của GitHub, mọi tệp tin có kích thước **vượt quá 100 MB** đều bị máy chủ từ chối tiếp nhận (Git Hard Size Limit).

Do đó, GitHub lưu trữ toàn bộ:
- Cấu hình kiến trúc mô hình (`config.json`).
- Cấu hình bộ tách từ (`tokenizer.json`, `tokenizer_config.json`).
- Mẫu hội thoại (`chat_template.jinja`).
- Cấu hình bộ mã hóa âm thanh (`audio_tokenizer/config.json`, `preprocessor_config.json`).
- Trạng thái mô hình kích hoạt (`active_model.txt`).

Còn tệp nhị phân trọng số lớn sẽ được tải tự động theo các phương án dưới đây.

---

## 🚀 2 Cách Để Sử Dụng Mô Hình

### Cách 1: Chạy Trên Cloud GPU (Kaggle Miễn Phí) — KHUYÊN DÙNG NHẤT 🌟
> **Ưu điểm:** Không cần tải 3 GB model về máy, không cần máy tính có card đồ họa GPU, máy yếu hoặc máy văn phòng vẫn chạy với tốc độ cực nhanh (~1.5s/câu).

1. Mở notebook `kaggle/OmDiOm.ipynb` trên [Kaggle](https://www.kaggle.com/).
2. Chọn **Settings** -> **Accelerator: GPU T4 x 2** -> **Internet: On**.
3. Chọn **Run All**. Notebook sẽ tự động tải model và cấp một đường dẫn **Cloudflare Tunnel** (ví dụ: `https://xxxx.trycloudflare.com`).
4. Mở `UI/index.html` trên máy bạn, vào mục **⚙ Cấu hình**, dán URL đường hầm vào là dùng được ngay lập tức!

---

### Cách 2: Tải Về Máy Để Chạy Hoàn Toàn Cục Bộ (Local Machine)
Nếu máy tính của bạn có card đồ họa NVIDIA (hoặc muốn chạy trên CPU), bạn chỉ cần chạy lệnh sau từ thư mục gốc của dự án:

```bash
python tools/tai_model.py
```

Lệnh này sẽ tự động tải toàn bộ trọng số từ kho Hugging Face chính thức về đặt đúng vị trí trong `models/OmniVoice` và `models/omdiom`.

Sau khi tải xong, bạn chỉ cần click đúp vào file `chay_local.bat` (Windows) hoặc chạy `bash chay_local.sh` (Linux/Mac) là hệ thống sẽ tự nạp model cục bộ và mở giao diện Studio.

