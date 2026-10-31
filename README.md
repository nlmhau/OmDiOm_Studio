# 🎙️ OmDiOm Studio — Hệ Thống Tổng Hợp & Nhân Bản Giọng Nói Tiếng Việt Zero-Shot

<p align="center">
  <img src="UI/assets/logo/rosette-256.png" width="120" height="120" alt="OmDiOm Studio Logo" style="border-radius:26px; box-shadow: 0 8px 24px rgba(0,0,0,0.12);"><br>
  <b>Nền Tảng AI Tổng Hợp, Nhân Bản & Thiết Kế Giọng Nói Tiếng Việt Chuyên Nghiệp</b><br>
  <i>Trang bị mô hình học sâu <b>OmDiOm</b> được huấn luyện lại chuyên sâu (Retrained / Fine-tuned) trên tập dữ liệu tiếng Việt quy mô lớn.</i>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue?logo=python" alt="Python">
  <img src="https://img.shields.io/badge/Framework-FastAPI-009688?logo=fastapi" alt="FastAPI">
  <img src="https://img.shields.io/badge/AI%20Core-PyTorch-EE4C2C?logo=pytorch" alt="PyTorch">
  <img src="https://img.shields.io/badge/Frontend-Neobrutalism%20UI-ffda39" alt="Frontend">
  <img src="https://img.shields.io/badge/License-Apache%202.0-green" alt="License">
</p>

---

## 🌟 Giới thiệu

**OmDiOm Studio** là hệ thống AI toàn diện phục vụ tổng hợp tiếng nói (Text-to-Speech - TTS), nhân bản giọng nói tức thời (Zero-Shot Voice Cloning) và thiết kế giọng nói theo câu lệnh mô tả (Voice Design) tối ưu riêng cho tiếng Việt.

Điểm khác biệt cốt lõi của hệ thống là sử dụng **mô hình OmDiOm được huấn luyện lại hoàn chỉnh trên tập ngữ liệu tiếng Việt** (thay vì sử dụng mô hình gốc `OmniVoice` vốn chỉ được huấn luyện sơ cấp), mang lại độ tự nhiên vượt trội, ngắt nghỉ đúng ngữ điệu 3 miền và hỗ trợ biểu cảm cảm xúc chân thực.

Hệ thống được thiết kế theo kiến trúc tách rời linh hoạt:
- **Core AI Engine:** Tích hợp mô hình học sâu **OmDiOm** (đã huấn luyện lại với trọng số safetensors tiếng Việt) kết hợp bộ mã hóa âm thanh `Boson Higgs Audio 2`, vận hành siêu tốc trên NVIDIA CUDA GPU (hoặc chế độ tối ưu trên CPU).
- **Backend API Server:** Viết bằng FastAPI hiệu năng cao, hỗ trợ sinh âm thanh đa luồng, xử lý ngắt nghỉ tự nhiên PCM, và quản lý thư viện giọng thông minh.
- **Giao diện Web Studio:** Thiết kế theo phong cách Neobrutalism hiện đại, giao diện trực quan, hỗ trợ kịch bản phân vai đa nhân vật, bộ thu âm tích hợp VAD, bộ tinh chỉnh âm thanh DSP và trình xem chi tiết phụ đề SRT mở rộng toàn màn hình.

---

## ✨ Tính năng nổi bật

### 1. 🗣️ Tổng Hợp Tiếng Nói (TTS) Với 7 Giọng Mẫu Tiếng Việt
- Tích hợp sẵn 7 giọng đọc đặc trưng trải dài 3 miền Bắc – Trung – Nam: **Cao Hùng, Linh Đức Tú, Minh Nhi, Minh Quý, Phương Thy, Tú Thành, Út Linh**.
- Thư viện giọng lưu trữ dưới dạng embedding tensor `.pt` siêu nhẹ (~10 KB/giọng), nạp tức thì trong vài phần trăm giây.

### 2. 🎭 Studio Kịch Bản Phân Vai Đa Nhân Vật (Dialogue Studio)
- Xây dựng hội thoại đa nhân vật chuyên nghiệp cho kịch bản phim, podcast, đọc truyện, phỏng vấn.
- Phân vai giọng đọc linh hoạt cho từng nhân vật, tự động ghép nối các lượt thoại kèm khoảng lặng tự nhiên (PCM zero-padding).
- Xuất đồng thời cả 3 tệp tiện ích: `.WAV` âm thanh, `.TXT` kịch bản và `.SRT` phụ đề khớp mốc thời gian từng câu thoại.

### 3. 🧬 Nhân Bản Giọng Nói Tức Thời (Zero-Shot Voice Cloning)
- Nhân bản đặc trưng giọng nói của bất kỳ ai chỉ từ **3 – 10 giây** âm thanh mẫu.
- Không cần huấn luyện lại mô hình (zero-shot inference), trích xuất acoustic prompt trực tiếp theo thời gian thực.

### 4. 🎨 Thiết Kế Giọng Nói Bằng Câu Lệnh (Voice Design)
- Tự động sáng tạo giọng nói mới hoàn toàn dựa trên mô tả ngôn ngữ tự nhiên (độ tuổi, giới tính, cao độ, phong cách phát âm).

### 5. 🎙️ Bộ Thu Âm Trực Tiếp Tích Hợp VAD (Voice Activity Detection)
- Thu âm giọng nói trực tiếp ngay trên trình duyệt mà không cần cài phần mềm ngoài.
- Thuật toán VAD tự động lọc khoảng lặng và cắt tỉa tạp âm đầu/cuối clip để chọn ra phân đoạn âm thanh chuẩn nhất làm mẫu nhân bản.

### 6. 🎛️ Bộ Xử Lý Tín Hiệu Âm Thanh DSP & Thẻ Cảm Xúc Tiếng Việt
- Hỗ trợ chèn thẻ cảm xúc tiếng Việt: `[cười]`, `[thở dài]`, `[ngạc nhiên]`, `[trầm trồ]`, `[nghi vấn]`, `[thắc mắc]`, `[đồng tình]`, `[bất mãn]`.
- Hỗ trợ cú pháp ngắt nghỉ chủ động: `[nghỉ: 0.5s]`, `[nghỉ: 1.0s]`.
- Bộ lọc DSP trực tiếp: Điều chỉnh cao độ (Pitch), tốc độ đọc (Speed), tăng độ dày trầm ấm (Bass Boost) trước khi lưu giọng vào thư viện.

---

## 📁 Cấu Trúc Dự Án

```
d:\OmDiOm\
├── chay_local.bat          # Kịch bản khởi chạy 1-Click tự động cho Windows
├── requirements.txt        # Danh sách thư viện Python cần thiết
├── README.md               # Tài liệu tổng quan và hướng dẫn sử dụng hệ thống
├── AGENTS.md               # Quy tắc vận hành và chỉ dẫn kỹ thuật
│
├── server/                 # Backend API (FastAPI)
│   ├── app.py              # Định tuyến REST API, xử lý upload & đồng bộ giọng
│   ├── engine.py           # Bộ nạp mô hình OmDiOm huấn luyện lại & thuật toán sinh âm thanh
│   ├── voices.py           # Quản lý thư viện giọng (.pt), quét đĩa & trích xuất metadata
│   └── system_info.py      # Tự động nhận diện phần cứng (CPU / NVIDIA CUDA GPU)
│
├── UI/                     # Giao diện Web Studio (Frontend)
│   ├── index.html          # Khung giao diện chính (Neobrutalism UI & Tabs)
│   ├── css/
│   │   └── style.css       # Bộ phong cách Neobrutalism, viền cứng & hiệu ứng động
│   └── js/
│       ├── app.js              # Điều phối sự kiện giao diện chính
│       ├── config.js           # Quản lý kết nối máy chủ và chuyển đổi mô hình OmDiOm
│       ├── dialogue-studio.js  # Logic kịch bản phân vai đa nhân vật
│       ├── file-manager.js     # Quản lý tệp & xuất audio/TXT/SRT
│       ├── audio-dsp.js        # Bộ xử lý âm thanh Web Audio API (Pitch, Speed, Bass)
│       ├── recorder.js         # Thu âm trình duyệt & thuật toán lọc VAD
│       ├── tts-engine.js       # Gọi API tổng hợp giọng nói
│       ├── voice-library.js    # Quản lý thư viện giọng mẫu & đồng bộ tự động
│       └── preview-modal.js    # Trình xem mở rộng toàn màn hình cho TXT & SRT
│
├── voices/                 # Thư viện 7 giọng mẫu tiếng Việt (.pt tensor)
│   ├── manifest.json       # Metadata danh sách giọng
│   └── *.pt                # Embedding vector của từng giọng nói
│
├── models/                 # Trọng số mô hình AI
│   └── omdiom/             # Trọng số mô hình OmDiOm huấn luyện lại (model.safetensors)
│
└── kaggle/                 # Triển khai Cloud GPU
    └── OmDiOm.ipynb        # Jupyter Notebook kết nối GPU T4x2 siêu tốc
```

---

## 🚀 Hướng Dẫn Cài Đặt & Khởi Chạy

### Cách 1: Khởi Chạy Cục Bộ (Local Machine) — Khuyên Dùng

Chạy tập lệnh khởi động nhanh 1-Click:

```powershell
D:\OmDiOm\chay_local.bat
```

Hệ thống sẽ tự động:
1. Kiểm tra môi trường Python và các thư viện trong `requirements.txt`.
2. Tự động nhận diện thiết bị khả dụng (NVIDIA CUDA GPU hoặc CPU đa lõi).
3. Nạp trọng số mô hình **OmDiOm** (tiếng Việt đã huấn luyện lại) vào bộ nhớ.
4. Khởi chạy máy chủ FastAPI tại `http://127.0.0.1:8000`.
5. Mở giao diện Studio tại `UI/index.html` trên trình duyệt mặc định.

---

### Cách 2: Khởi Chạy Trên Cloud GPU (Kaggle Miễn Phí)

Đối với máy tính không có GPU rời, bạn có thể chạy phần tính toán AI trên Cloud GPU:

1. Đăng nhập [Kaggle](https://www.kaggle.com/) và tạo Notebook mới.
2. Chọn **File -> Import Notebook** -> chọn tệp `kaggle/OmDiOm.ipynb`.
3. Cài đặt môi trường Kaggle:
   - **Accelerator:** `GPU T4 x 2`
   - **Internet:** `On`
4. Chọn **Run All**. Ô cuối sẽ sinh ra **Cloudflare Tunnel URL** và **API KEY**:
   ```
   ┌─ DÁN VÀO GIAO DIỆN ──────────────────────────┐
   │ LINK : https://your-tunnel-subdomain.trycloudflare.com
   │ KEY  : your-secret-api-key
   └──────────────────────────────────────────────┘
   ```
5. Mở giao diện `UI/index.html` trên máy bạn, vào ô **⚙ Cấu hình**, dán URL + KEY vào và bấm **Lưu & Kết nối**. Hệ thống sẽ tự động chuyển sang vận hành bằng GPU Kaggle với tốc độ sinh âm thanh siêu tốc (~1–2 giây/câu).

---

## 📡 Bảng Tra Cứu REST API

Máy chủ cung cấp đầy đủ các chuẩn API RESTful để dễ dàng tích hợp:

| Phương thức | Đường dẫn | Chức năng | Tham số chính |
|---|---|---|---|
| `GET` | `/health` | Kiểm tra tình trạng server, model OmDiOm và thiết bị đang chạy | Không |
| `GET` | `/api/system/status` | Thông tin chi tiết phần cứng (CPU, GPU, RAM, VRAM) | Không |
| `GET` | `/api/voices` | Danh sách toàn bộ các giọng mẫu hiện có | Không |
| `GET` | `/api/voices/bundle` | Đóng gói toàn bộ file giọng mẫu (.pt) để đồng bộ lên máy chủ GPU | Không |
| `POST` | `/api/voices/sync` | Đồng bộ gói giọng đọc vào thư viện trên server | `bundle` (JSON) |
| `POST` | `/api/tts` | Tổng hợp giọng nói từ văn bản kèm thẻ cảm xúc | `text`, `voice`, `num_step`, `speed` |
| `POST` | `/api/clone` | Nhân bản giọng từ clip mẫu | `text`, `ref_audio`, `ref_text` |
| `POST` | `/api/design` | Thiết kế giọng từ mô tả ngôn ngữ tự nhiên | `text`, `instruct` |
| `POST` | `/api/dialogue/synthesize` | Tổng hợp kịch bản phân vai đa nhân vật | Mảng các `lines`, `pause_ms` |
| `POST` | `/api/voices/upload` | Tải lên file giọng `.pt` mới vào thư viện | `file` (multipart/form-data) |

---

## 👥 Danh Mục 7 Giọng Mẫu Tiếng Việt

| Mã định danh | Tên hiển thị | Vùng miền | Đặc trưng âm sắc | Tệp embedding |
|---|---|---|---|---|
| `Cao_Hung` | Cao Hùng | Miền Nam | Trầm ấm, truyền cảm, dạn dày | `Cao_Hùng.pt` |
| `Linh_Duc_Tu` | Linh Đức Tú | Miền Bắc | Rõ ràng, chuẩn mực tin tức | `Linh_Dục_Tú.pt` |
| `Minh_Nhi` | Minh Nhi | Miền Nam | Ngây thơ, hoạt bát, trẻ em | `Minh_Nhi.pt` |
| `Minh_Quy` | Minh Quý | Miền Trung | Thanh niên, rõ ràng, dứt khoát | `Minh_Quý.pt` |
| `Phuong_Thy` | Phương Thy | Miền Nam | Sâu lắng, truyền cảm, dẫn truyện | `Phương_Thy.pt` |
| `To_Thanh` | Tô Thành | Miền Bắc | Lôi cuốn, nhịp nhàng, kể chuyện | `Tô_Thành.pt` |
| `Ut_Linh` | Út Linh | Miền Tây | Ma mị, huyền bí, kịch tính | `Út_Linh.pt` |

---

## ⚖️ Bản Quyền & Cam Kết Đạo Đức Dữ Liệu (Ethics)

- **Mô hình cốt lõi:** Mô hình **OmDiOm** được huấn luyện lại chuyên sâu trên tập dữ liệu tiếng Việt quy mô lớn, phát triển trên nền tảng kiến trúc học sâu tiên tiến.
- **Bộ mã hóa âm thanh:** `Boson Higgs Audio 2` (Theo giấy phép Boson Higgs Audio License).
- **Quyền riêng tư dữ liệu giọng nói:** 7 tệp embedding `.pt` là dữ liệu giọng nói được thu âm và xử lý chuẩn hóa có sự đồng thuận của người đọc. Nghiêm cấm sử dụng hệ thống vào các mục đích mạo danh lừa đảo hoặc vi phạm pháp luật.

---
<p align="center">
  <b>OmDiOm Studio — Vietnamese Voice AI Platform</b><br>
  <i>Phát triển & Tối ưu hóa năm 2026</i>
</p>
