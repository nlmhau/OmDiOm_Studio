# 📖 HƯỚNG DẪN CÀI ĐẶT VÀ VẬN HÀNH TOÀN DIỆN · OMDIOM STUDIO

Chào mừng bạn đến với **OmDiOm Studio** — Nền tảng Trí tuệ Nhân tạo Tổng hợp tiếng nói và Nhân bản giọng nói tiếng Việt Zero-Shot chuyên nghiệp, ứng dụng mô hình tạo sinh học sâu **OmniVoice** kết hợp bộ trọng số tinh chỉnh tiếng Việt **OmDiOm-ft-4000**.

Tài liệu này cung cấp hướng dẫn đầy đủ từ A-Z giúp bất kỳ ai (dù không có card đồ họa GPU rời) cũng có thể tải về, cài đặt và trải nghiệm mượt mà 100% mọi chức năng của hệ thống.

---

## 🌟 MỤC LỤC HƯỚNG DẪN

1. [Cấu Trúc Thư Mục Dự Án](#1-cấu-trúc-thư-mục-dự-án)
2. [Cách 1: Chạy Miễn Phí Trên Cloud GPU (Kaggle) — Khuyên Dùng Cho Mọi Máy 🌟](#2-cách-1-chạy-miễn-phí-trên-cloud-gpu-kaggle--khuyên-dùng-cho-mọi-máy-)
3. [Cách 2: Chạy Hoàn Toàn Cục Bộ (Local Machine)](#3-cách-2-chạy-hoàn-toàn-cục-bộ-local-machine)
4. [Hướng Dẫn Sử Dụng Chi Tiết Các Chức Năng Studio](#4-hướng-dẫn-sử-dụng-chi-tiết-các-chức-năng-studio)
5. [Khắc Phục Sự Cố Thường Gặp (FAQ & Troubleshooting)](#5-khắc-phục-sự-cố-thường-gặp-faq--troubleshooting)

---

## 1. CẤU TRÚC THƯ MỤC DỰ ÁN

```
OmDiOm_Studio/
├── UI/                         # Giao diện Web Studio hiện đại (HTML5/Vanilla JS/Canvas)
│   ├── index.html              # Trang Studio chính
│   ├── css/style.css           # Giao diện Neobrutalism cao cấp
│   ├── js/                     # Các module điều khiển audio, DSP, kịch bản, thu âm
│   └── assets/logo/            # Nhận diện thương hiệu Rosette & Logo
│
├── server/                     # Máy chủ điều phối Gateway (FastAPI)
│   ├── app.py                  # Các RESTful API Endpoints
│   ├── engine.py               # Lớp điều phối mô hình học sâu PyTorch
│   ├── voices.py               # Quản lý thư viện giọng và tệp .pt
│   └── system_info.py          # Đo đạc thông số CPU, GPU, VRAM thời gian thực
│
├── voices/                     # Thư viện 7 giọng chuẩn tiếng Việt (đã nhúng sẵn)
│   ├── manifest.json           # Danh bạ 7 giọng đọc 3 miền
│   ├── Cao_Hùng.pt             # Giọng Nam Bắc trầm ấm
│   ├── Út_Linh.pt              # Giọng Nữ Nam ngọt ngào
│   ├── Minh_Nhi.pt             # Giọng Nam Nam vui nhộn
│   ├── Tô_Thành.pt             # Giọng Nam Bắc truyền cảm
│   ├── Phương_Thy.pt           # Giọng Nữ Bắc trẻ trung
│   ├── Minh_Quý.pt             # Giọng Nam Trung chuẩn Huế
│   └── Linh_Dục_Tú.pt          # Giọng Nữ Trung thanh thoát
│
├── kaggle/                     # Khởi chạy Cloud GPU miễn phí
│   ├── OmDiOm.ipynb            # Notebook tự động mở máy chủ GPU T4x2 + Cloudflare Tunnel
│   └── OmDiOm.json             # Cấu hình Kaggle API
│
├── models/                     # Thư mục lưu trữ cấu hình & trọng số mô hình
│   ├── README.md               # Hướng dẫn chi tiết về file trọng số
│   ├── active_model.txt        # Lựa chọn model hoạt động
│   ├── omdiom/                 # Cấu hình OmDiOm tiếng Việt
│   └── OmniVoice/              # Cấu hình OmniVoice Base
│
├── tools/                      # Các công cụ hỗ trợ
│   └── tai_model.py            # Script tự động tải model từ Hugging Face
│
├── chay_local.bat              # Script 1-Click khởi chạy máy chủ trên Windows
├── chay_local.sh               # Script 1-Click khởi chạy máy chủ trên Linux/macOS
├── requirements.txt            # Danh sách thư viện Python cần thiết
└── README.md                   # Trang thông tin tổng quan GitHub
```

---

## 2. CÁCH 1: CHẠY MIỄN PHÍ TRÊN CLOUD GPU (KAGGLE) — KHUYÊN DÙNG CHO MỌI MÁY 🌟

> **Lý do khuyên dùng:** Mô hình tạo sinh giọng nói yêu cầu tính toán ma trận GPU nặng. Chạy trên Kaggle giúp bạn tận dụng **GPU Tesla T4 (16GB VRAM)** hoàn toàn miễn phí, sinh âm thanh trong **1–2 giây/câu** mà không cần tải 3 GB model về máy, không phụ thuộc vào cấu hình máy tính cá nhân.

### Các bước thực hiện:

#### Bước 1: Chuẩn bị trên Kaggle
1. Truy cập [Kaggle](https://www.kaggle.com/) và đăng nhập (nếu chưa có tài khoản, đăng ký miễn phí trong 1 phút).
2. Nhấn nút **Create** -> **New Notebook**.
3. Chọn menu **File** -> **Import Notebook** -> Tải lên tệp `kaggle/OmDiOm.ipynb` từ mã nguồn bạn vừa tải về.

#### Bước 2: Bật GPU và Kết nối mạng Internet
Ở bảng điều khiển bên phải màn hình Kaggle (**Notebook options**):
- **Accelerator:** Chọn **GPU T4 x 2** (hoặc GPU T4 x 1).
- **Internet:** Bật **On** (bắt buộc để tải thư viện và mở đường hầm).

#### Bước 3: Khởi chạy toàn bộ (Run All)
- Nhấn nút **Run All** (hoặc phím tắt `Ctrl + F10`).
- Notebook sẽ tự động:
  1. Cài đặt các gói thư viện cần thiết.
  2. Nạp mô hình học sâu lên GPU Tesla T4.
  3. Khởi động máy chủ backend FastAPI.
  4. Mở đường hầm bảo mật HTTPS công khai bằng Cloudflare Tunnel.

#### Bước 4: Lấy thông tin kết nối
Khi ô số 6 hoặc số 7 chạy xong, cuộn xuống dưới bạn sẽ thấy khung thông báo nổi bật dạng:

```
┌────────────────────────────────────────────────────────────────────────┐
│  OMDIOM STUDIO - THÔNG TIN KẾT NỐI GPU CLOUD                          │
├────────────────────────────────────────────────────────────────────────┤
│  ĐƯỜNG DẪN CLOUDFLARE : https://xxxx-xxxx-xxxx.trycloudflare.com       │
│  MÃ BẢO MẬT (API KEY) : testkey                                        │
└────────────────────────────────────────────────────────────────────────┘
```

👉 Hãy sao chép (Copy) đường link `https://...trycloudflare.com` này.

#### Bước 5: Kết nối vào Giao diện Studio
1. Trên máy tính của bạn, mở tệp `UI/index.html` bằng trình duyệt web bất kỳ (Chrome, Edge, Cốc Cốc, Firefox).
2. Nhấn vào nút **⚙ Cấu hình** ở góc trên bên phải thanh tiêu đề.
3. Trong mục **Địa chỉ máy chủ (Server URL)**: Dán link Cloudflare vừa copy ở Bước 4 vào.
4. Trong mục **API Key**: Điền `testkey`.
5. Nhấn **Lưu & Kết nối**.
6. Khi thấy đèn trạng thái ở góc trên chuyển sang màu **Xanh lá (ONLINE - GPU Tesla T4)**, hệ thống đã sẵn sàng 100%!

---

## 3. CÁCH 2: CHẠY HOÀN TOÀN CỤC BỘ (LOCAL MACHINE)

Dành cho những người dùng có máy tính cá nhân trang bị card đồ họa rời NVIDIA (khuyến nghị tối thiểu 8GB VRAM) hoặc muốn thử nghiệm trên CPU.

### Bước 1: Cài đặt Python và môi trường
- Yêu cầu: Python phiên bản từ **3.10 trở lên** (khuyến nghị Python 3.10 hoặc 3.11).
- Mở Terminal hoặc Command Prompt tại thư mục dự án `OmDiOm_Studio`:

```bash
pip install -r requirements.txt
```

*Lưu ý:* Nếu bạn có card GPU NVIDIA, hãy cài đặt phiên bản PyTorch hỗ trợ CUDA tương ứng:
```bash
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu121
```

### Bước 2: Tải trọng số mô hình về máy
Chạy script tự động tải trọng số:
```bash
python tools/tai_model.py
```
Script sẽ tự động kết nối Hugging Face và tải toàn bộ mô hình về thư mục `models/`.

### Bước 3: Khởi chạy máy chủ cục bộ
- **Trên Windows:** Chỉ cần click đúp vào file `chay_local.bat`.
- **Trên Linux/macOS:** Mở terminal và chạy `bash chay_local.sh`.

Máy chủ sẽ lắng nghe tại `http://127.0.0.1:8000`.

### Bước 4: Mở giao diện
Mở file `UI/index.html` trên trình duyệt. Trong mục **⚙ Cấu hình**, để địa chỉ mặc định `http://127.0.0.1:8000` và API Key `testkey`, sau đó bấm **Lưu & Kết nối**.

---

## 4. HƯỚNG DẪN SỬ DỤNG CHI TIẾT CÁC CHỨC NĂNG STUDIO

### Chức năng 1 · Văn bản → Giọng nói (TTS với 7 giọng mẫu)
1. Chọn tab **Văn bản → Giọng** trên thanh điều hướng.
2. Nhập văn bản tiếng Việt cần đọc vào ô soạn thảo.
3. Chọn giọng đọc mong muốn trong số 7 giọng mẫu có sẵn:
   - **Cao Hùng (Nam Bắc):** Trầm ấm, chững chạc, thích hợp đọc tin tức thời sự.
   - **Út Linh (Nữ Nam):** Dịu dàng, truyền cảm, thích hợp đọc truyện tâm lý, tự sự.
   - **Minh Nhí (Nam Nam):** Vui vẻ, sôi nổi, thích hợp lồng tiếng hoạt hình, quảng cáo.
   - **Tô Thành (Nam Bắc):** Sâu lắng, đĩnh đạc, đọc tiểu thuyết dài tập.
   - **Phương Thy (Nữ Bắc):** Tươi trẻ, rõ ràng, phù hợp làm trợ lý ảo, podcast.
   - **Minh Quý (Nam Trung):** Chuẩn giọng Huế, mộc mạc, phóng sự đời sống.
   - **Linh Dục Tú (Nữ Trung):** Nhẹ nhàng, thanh thoát, ngâm thơ, ca từ nghệ thuật.
4. **Chèn thẻ biểu cảm:** Nhấp vào các nút cảm xúc nhanh phía dưới ô văn bản:
   - `[cười]` / `[cuoi]`: Chèn ngữ điệu cười tự nhiên.
   - `[thở dài]`: Chèn tiếng thở dài tâm trạng.
   - `[ngạc nhiên]`: Giọng thảng thốt, bất ngờ.
   - `[ngắt nghỉ:0.5s]`: Chèn khoảng im lặng chuẩn 500 mili-giây.
5. Nhấn nút **✦ Tạo giọng nói**. Sau 1–2 giây, âm thanh sẽ phát ngay kèm đồ thị sóng âm trực quan. Bạn có thể nhấn nút **↓ .WAV** để tải tệp âm thanh hoặc **⏱️ .SRT** để lấy tệp phụ đề.

---

### Chức năng 2 · Nhân bản giọng nói Zero-Shot (Voice Cloning)
1. Chọn mục **Nhân bản & đọc** trên thanh điều hướng.
2. Cung cấp một đoạn âm thanh mẫu người nói (từ 3 đến 10 giây) bằng một trong hai cách:
   - **Cách A - Tải tệp lên:** Nhấn ô tải tệp và chọn file `.wav` hoặc `.mp3`.
   - **Cách B - Thu âm trực tiếp:** Nhấn nút **🎙️ Bắt đầu ghi**, nói một câu vào micro máy tính, sau đó nhấn **⏹ Dừng ghi**.
3. **Cắt đoạn sạch (Audio Trimmer):** Sử dụng 2 thanh trượt trên đồ thị sóng âm để cắt lấy khoảng thời gian phát âm rõ ràng nhất (loại bỏ tiếng ồn đầu/cuối).
4. Nhập nội dung văn bản mới bạn muốn giọng nói đó phát âm.
5. Nhấn **✦ Nhân bản & đọc**. Mô hình sẽ trích xuất đặc trưng giọng và tái tạo lại chính xác âm sắc người đó với nội dung mới!

---

### Chức năng 3 · 🎭 Studio Kịch bản Phân vai Đa nhân vật (Dialogue Studio)
1. Chọn tab **🎭 Studio phân vai**.
2. Thêm các dòng hội thoại kịch bản:
   - Dòng 1: Chọn nhân vật A (gán giọng *Út Linh*), nhập lời thoại hỏi: *"Chào anh, hôm nay anh có khỏe không?"*.
   - Dòng 2: Chọn nhân vật B (gán giọng *Cao Hùng*), nhập lời thoại đáp: *"Cảm ơn em, anh vẫn khỏe!"*.
3. Bạn có thể thêm không giới hạn các lượt đối thoại, thay đổi khoảng lặng chuyển tiếp giữa các câu thoại (mặc định 300ms).
4. Nhấn **✦ Tạo âm thanh kịch bản đối thoại**.
5. Hệ thống sẽ tuần tự sinh âm thanh cho từng nhân vật và tự động ghép nối thành một tệp âm thanh đồng nhất.
6. Bạn có thể tải về đồng thời:
   - **Tệp âm thanh hội thoại (.WAV)**
   - **Tệp kịch bản lời thoại (.TXT)**
   - **Tệp phụ đề chuẩn thời gian (.SRT)** sẵn sàng kéo thả vào phần mềm dựng phim (Premiere, CapCut).

---

## 5. KHẮC PHỤC SỰ CỐ THƯỜNG GẶP (FAQ & TROUBLESHOOTING)

### Câu hỏi 1: Tôi tải về và chạy cục bộ, thấy thông báo "MOCK MODE — không nạp model thật" là sao?
- **Nguyên nhân:** Máy tính của bạn chưa có thư viện `torch` hoặc `omnivoice`, hoặc chưa có file trọng số `model.safetensors` trong `models/`.
- **Cách giải quyết:** 
  1. Nếu muốn chạy nhanh nhất không cần cài đặt nặng: Chuyển sang **Cách 1 (Chạy qua Kaggle GPU)** — chỉ mất 2 phút là có ngay máy chủ GPU thật.
  2. Nếu muốn chạy máy tính thật: Chạy `pip install -r requirements.txt` và `python tools/tai_model.py`.

### Câu hỏi 2: Link Cloudflare Tunnel bị báo lỗi không kết nối được?
- **Nguyên nhân:** Phiên làm việc trên Kaggle đã bị ngắt do bạn đóng tab hoặc để quá thời gian chờ (idle timeout).
- **Cách giải quyết:** Mở lại Notebook trên Kaggle, nhấn **Run All**, lấy link Tunnel mới và cập nhật lại vào ô **⚙ Cấu hình** trên giao diện Studio.

### Câu hỏi 3: Tôi ấn phát âm thanh nhưng trình duyệt không kêu?
- **Nguyên nhân:** Một số trình duyệt (đặc biệt là Chrome) áp dụng chính sách chặn tự động phát âm thanh (Autoplay Policy) khi người dùng chưa tương tác với trang web.
- **Cách giải quyết:** Bạn chỉ cần nhấp chuột bất kỳ vào trang giao diện rồi nhấn nút **Play (▶)** trên thanh phát âm thanh.

---

<p align="center">
  <b>OmDiOm Studio — Vietnamese Voice AI Platform</b><br>
  <i>Đồ án chuyên đề Trí tuệ nhân tạo · Phân hiệu Trường Đại học Thủy Lợi · Năm 2026</i>
</p>

