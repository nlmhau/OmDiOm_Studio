# KHUNG BÁO CÁO — Nghiên cứu và ứng dụng mô hình học sâu trong tổng hợp, nhân bản giọng nói tiếng Việt zero-shot

*Điền số liệu thật sau khi chạy `eval/`. Các ô `[...]` là chỗ cần điền.*

---

## Mở đầu

**Đề tài:** Nghiên cứu và ứng dụng mô hình học sâu trong tổng hợp, nhân bản giọng nói tiếng Việt zero-shot.

**Lý do chọn:** VoiceStudio là dự án mã nguồn mở đạt ~28.000 sao GitHub, giải quyết bài toán thực tế (nhân bản giọng nói không cần huấn luyện) bằng kiến trúc diffusion language model. Tuy nhiên repo gốc là một **sản phẩm thương mại** với 14 engine và ~60 dependency — không phù hợp để nghiên cứu một model cụ thể. Đề tài này tách riêng một model, đánh giá nó một cách có hệ thống.

**Mục tiêu:**
1. Dựng lại được pipeline suy luận với **một** model (`k2-fsa/OmniVoice`)
2. Xây dựng giao diện sử dụng được, chạy local
3. Đánh giá định lượng chất lượng và tốc độ trên tiếng Việt
4. So sánh đánh đổi giữa chất lượng và chi phí tính toán

---

## 1. Cơ sở lý thuyết

### 1.1. Tổng hợp giọng nói zero-shot

*[Trình bày: TTS truyền thống cần dataset + training cho từng giọng; zero-shot dùng một encoder để trích speaker embedding từ clip ngắn rồi điều kiện hoá quá trình sinh.]*

### 1.2. Kiến trúc OmniVoice

*[Mô tả: model sinh token rời rạc theo cơ chế masked diffusion — khởi tạo toàn bộ chuỗi ở trạng thái mask rồi "mở khoá" dần qua `num_step` bước. Đây là lý do `num_step` là tham số then chốt đánh đổi chất lượng ↔ tốc độ.]*

Các tham số chính:

| Tham số | Vai trò | Mặc định |
|---|---|---|
| `num_step` | Số bước khử nhiễu | 32 (app dùng 16) |
| `guidance_scale` | Classifier-free guidance | 2.0 |
| `t_shift` | Dịch lịch nhiễu | 0.1 |
| `speed` / `duration` | Kiểm soát độ dài | 1.0 / None |
| `position_temperature` | Độ ngẫu nhiên vị trí mask | 5.0 |

### 1.3. Ba chế độ suy luận

- **TTS**: chỉ văn bản → giọng mặc định
- **Voice cloning**: văn bản + clip mẫu + transcript → giọng của clip
- **Voice design**: văn bản + mô tả thuộc tính → giọng theo yêu cầu

---

## 2. Phương pháp

### 2.1. Kiến trúc hệ thống

*[Chèn sơ đồ: UI (local) → HTTPS → FastAPI (Kaggle GPU) → OmniVoice]*

**Lý do tách client/server:** model cần GPU ~2,5 GB VRAM; máy cá nhân thường không có. Kaggle cung cấp T4 miễn phí (30h/tuần). Giao diện chạy local nên dữ liệu văn bản không phải rời máy dưới dạng phụ thuộc dịch vụ bên thứ ba.

### 2.2. Tối giản hoá

| Hạng mục | Gốc | Bản này |
|---|---|---|
| Dòng code Python (app) | ~120.000 | **[≈ 600]** |
| Dependency | ~60 | **6** |
| Engine | 14 | **1** |

*[Điền số dòng thật bằng `wc -l server/*.py ui/index.html`]*

### 2.3. Thiết lập thực nghiệm

- **Phần cứng:** Kaggle, 1× NVIDIA Tesla T4 (16 GB), 4 vCPU, 29 GB RAM
- **Phần mềm:** Python 3.11, PyTorch [x.x], transformers [x.x]
- **Dữ liệu:** 5 câu tiếng Việt, độ dài 30–220 ký tự, có dấu, có số và tên riêng

---

## 3. Kết quả

### 3.1. Thí nghiệm 1 — Ảnh hưởng của `num_step`

*[Điền từ `bench_numstep.csv`]*

| num_step | Thời gian sinh TB (s) | RTF TB | Chậm hơn so với 8 |
|---|---|---|---|
| 8 | | | 1.00× |
| 16 | | | |
| 32 | | | |
| 64 | | | |

**Nhận xét:** *[Ví dụ: từ 8→16 thời gian tăng 1,65× nhưng chất lượng cải thiện rõ; từ 32→64 thời gian tăng 5,57× mà chất lượng gần như không đổi → 16 là điểm tối ưu cho ứng dụng thời gian thực.]*

### 3.2. Thí nghiệm 2 — Độ dài clip mẫu

*[Điền từ `eval_clone.csv`]*

| Độ dài clip | Cosine similarity | Nhận xét |
|---|---|---|
| 3 s | | |
| 5 s | | |
| 10 s | | |
| 15 s | | |

**Nhận xét:** *[...]*

### 3.3. Chất lượng tiếng Việt

*[Phần quan trọng nhất — đánh giá chủ quan]*

| Tiêu chí | Điểm 1–5 | Ghi chú |
|---|---|---|
| Độ rõ chữ | | |
| Đúng dấu thanh (hỏi/ngã/nặng) | | |
| Ngắt nghỉ tự nhiên | | |
| Xử lý số và từ ngoại lai | | |
| Độ tự nhiên tổng thể | | |

**Các lỗi quan sát được:** *[liệt kê cụ thể — đây là phần có giá trị nhất của báo cáo]*

### 3.4. Hiệu năng tài nguyên

| | |
|---|---|
| VRAM đỉnh | [~2.5] GB |
| Thời gian nạp model | [...] s |
| Thời gian khởi động server | [...] s |

---

## 4. Thảo luận

### 4.1. Điểm mạnh
- Zero-shot: không cần dữ liệu huấn luyện cho giọng mới
- Chạy được trên GPU phổ thông (T4 16 GB, thậm chí ~4 GB)
- Đa ngôn ngữ trong cùng một model

### 4.2. Hạn chế
- *[Chất lượng tiếng Việt — nêu trung thực]*
- Không kiểm soát được cảm xúc/ngữ điệu chi tiết
- Phụ thuộc chất lượng clip mẫu: nhiễu/vọng bị "sao chép" sang kết quả
- Không có cơ chế chống lạm dụng (deepfake)

### 4.3. Đạo đức
Model có thể bị dùng để giả mạo giọng nói. Các biện pháp trong phạm vi đồ án: không phát hành public endpoint, yêu cầu API key, ghi rõ giới hạn trong tài liệu.

---

## 5. Kết luận

*[Tóm tắt 3–4 câu: đã làm được gì, con số chính, kết luận về đánh đổi.]*

**Hướng phát triển:**
- Fine-tune trên dataset tiếng Việt
- Thêm watermark để truy xuất nguồn gốc
- Lượng hoá (int8/GGUF) để chạy trên CPU

---

## Phụ lục

- **A.** Hướng dẫn cài đặt & chạy (từ `README.md`)
- **B.** Toàn bộ mã nguồn
- **C.** CSV kết quả thô
- **D.** Link video demo

---

## Tài liệu tham khảo

1. Zhu, H. et al. *OmniVoice*. Xiaomi Corp., 2026. `k2-fsa/OmniVoice`, Apache-2.0.
2. Debpalash. *VoiceStudio*. GitHub, 2026. AGPL-3.0.
3. *[Bổ sung: bài báo về zero-shot TTS, masked diffusion language model, đánh giá speaker similarity bằng ECAPA-TDNN]*
