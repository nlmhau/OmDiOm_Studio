# Dữ liệu thật sự lấy từ đâu

*Trả lời câu hỏi trực tiếp: nguồn dữ liệu cụ thể cho từng phần của đồ án.*

---

## 0. Nói thẳng trước

**Con số "≥300 câu, ≥20 clip, ≥10 người nói" trong phiếu là mình tự đặt ra — không phải lấy từ đâu cả.** Đó là *chỉ tiêu* để bạn cam kết với thầy, không phải dữ liệu đã có sẵn.

Bạn hiện **chưa có một file dữ liệu nào**. Dưới đây là các nguồn thật để lấy.

---

## 1. Điều quan trọng nhất: bạn KHÔNG cần dữ liệu huấn luyện

OmniVoice là **zero-shot** — model đã được huấn luyện sẵn (2,3 GB trên HuggingFace). Bạn **không train lại**, không fine-tune.

Nên "dữ liệu" của đồ án chỉ gồm **3 loại đầu vào để đánh giá**:

| Loại | Số lượng trong phiếu | Có sẵn trên mạng? |
|---|---|---|
| **A.** Câu văn bản để test | ≥ 300 câu | ❌ Không có sẵn bộ phủ dấu thanh — phải tự tạo |
| **B.** Clip giọng mẫu | ≥ 20 clip, ≥ 10 người | ✅ **Có sẵn** (VIVOS, Common Voice…) |
| **C.** Điểm MOS | ≥ 10 người nghe | ❌ Phải tự thu — không bao giờ có sẵn |

Hiểu được điều này là bớt lo đi một nửa: **chỉ có phần A và C là việc của bạn**, phần B tải về trong 10 phút.

---

## 2. Phần B — Clip giọng mẫu (dễ nhất)

### ⭐ Lựa chọn 1: VIVOS — nguồn tốt nhất cho đồ án này

| | |
|---|---|
| Nội dung | **15 giờ** đọc tiếng Việt, **65 người nói** (34 nam, 31 nữ) |
| Chất lượng | 16 kHz, phòng yên tĩnh, micro tốt, ghi từng câu một |
| Transcript | **Có sẵn** — khỏi phải tự ghi lại lời |
| Giấy phép | CC BY-NC-SA 4.0 (phi thương mại — **đúng mục đích đồ án**) |
| Tải về | HuggingFace: `AILAB-VNUHCM/vivos` · hoặc Zenodo `7068130` (1,5 GB) |
| Nguồn gốc | AILAB, ĐH Khoa học Tự nhiên – ĐHQG TP.HCM, 2016 |

**Vì sao hợp với đề tài:** bạn cần ≥10 người nói, VIVOS có **65 người**. Chỉ cần lấy 15 giây đầu của 10 người bất kỳ là xong phần B trong một buổi chiều.

**Cách lấy clip:**
```python
from datasets import load_dataset, Audio
ds = load_dataset("AILAB-VNUHCM/vivos", split="train")
ds = ds.cast_column("audio", Audio(sampling_rate=16000))

# Lấy 1 clip mỗi người cho 10 người đầu tiên
seen = set()
for row in ds:
    spk = row["speaker_id"]
    if spk in seen: continue
    seen.add(spk)
    # cắt 15 giây đầu, lưu làm clip gốc
    ...
    if len(seen) >= 10: break
```

### Lựa chọn 2: Tự thu — nên làm song song

10 người = 3 bạn trong nhóm + bạn bè/gia đình. Ghi bằng điện thoại, phòng yên tĩnh, 15–20 giây/người.

**Ưu điểm:** kiểm soát 100% chất lượng · có consent rõ ràng · không vướng giấy phép · **thú vị hơn khi bảo vệ** (dùng chính giọng mình làm demo).

**Khuyến nghị:** dùng **cả hai** — 10 người từ VIVOS + 3 bạn trong nhóm = 13 người nói. Trong báo cáo tách riêng 2 nhóm để so sánh (giọng thu studio vs. giọng ghi điện thoại).

### Lựa chọn 3: Mozilla Common Voice (vi)
CC0 — thoải mái nhất về giấy phép. Nhưng chất lượng **không đều** (nhiều clip ghi bằng điện thoại, có nhiễu). Dùng khi cần giấy phép thương mại.

### ⛔ Cẩn thận với 2 nguồn này

| Dataset | Vấn đề |
|---|---|
| **viet-tts-dataset (ntt123)** | 35,9 giờ nhưng **audio là do Google TTS tổng hợp**, không phải giọng người thật. Dùng làm clip mẫu là sai hoàn toàn — bạn đang clone giọng máy bằng giọng máy. |
| **viVoice (1000h)** | Thiết kế cho TTS multi-speaker, rất tốt — nhưng **giấy phép ghi là "unknown"**. Không nên đưa vào đồ án nộp cho trường. |

---

## 3. Phần A — 300 câu văn bản (việc chính của bạn)

**Không có dataset nào trên mạng có sẵn "300 câu phủ đủ 6 thanh điệu tiếng Việt".** Đây là phần bạn phải tự tạo — và cũng chính là **đóng góp riêng của đồ án**.

### Cách làm: sinh bằng template

Tiếng Việt có 6 thanh: **ngang · huyền · sắc · hỏi · ngã · nặng**

Chiến lược: mỗi câu phải chứa **nhiều từ cùng một thanh** để dễ phát hiện model đọc sai thanh nào.

Ví dụ cho thanh **ngã**:
```
"Vĩnh viễn những kỷ niệm đẹp vẫn mãi ở lại trong ký ức."
"Bão lũ đã tàn phá những cánh đồng lúa mỹ mãn."
```

Ví dụ cho thanh **hỏi**:
```
"Bạn có thể chỉ giúp tôi chỗ gửi xe ở đâu không?"
"Cuốn sách ấy để ở trên kệ, bạn lấy giúp tôi nhé."
```

### Cấu trúc file dữ liệu cần tạo

```csv
sentence_id,speaker_id,thanh_trong_tam,noi_dung,do_dai_ky_tu,cum_danh_tu
S0001,,hoi,"Bạn có thể chỉ giúp tôi chỗ gửi xe ở đâu không?",46,
S0002,,nga,"Vĩnh viễn những kỷ niệm đẹp vẫn mãi ở lại trong ký ức.",57,
S0003,,sac,"Chúc mừng năm mới, chúc bạn sức khỏe và thành công.",52,
...
```

**Chỉ tiêu thực tế:** 300 câu = **50 câu × 6 thanh**. Bạn có thể viết 10 câu mẫu cho mỗi thanh, rồi biến đổi từ vựng để ra 50. Hoặc mình viết script sinh tự động cho bạn.

### Nguồn text tham khảo (nếu cần thêm)
- **Wikipedia tiếng Việt** (CC BY-SA) — câu văn tự nhiên, đa dạng
- **PhoATIS, VnCoreNLP corpus** — dùng cho NLP, không phải cho đọc

Nhưng lời khuyên: **tự viết vẫn tốt hơn**, vì bạn kiểm soát được thanh điệu.

---

## 4. Phần C — Điểm MOS (khó nhất, không thể tải về)

Không có sẵn. Bạn phải tự tổ chức.

### Kế hoạch tối thiểu
| | |
|---|---|
| Người nghe | **≥ 10 người**, phải **ngoài nhóm** (đây là yêu cầu của thầy) |
| Mẫu chấm | ~50 file audio, **xáo trộn ngẫu nhiên**, ẩn danh (không biết cấu hình nào tạo ra) |
| Thang điểm | MOS 1–5 chuẩn (1 = rất tệ, 5 = như người thật) |
| Thời gian | ~20 phút/người |
| Cách chạy | Google Form + link Drive, hoặc web app tự làm |

### Cảnh báo thực tế
Đây là chỗ **dễ trượt nhất**. Nhờ 10 người ngồi nghe 50 file trong 9 ngày là việc khó. Nếu không xoay được người ngoài, hãy **nói trước với thầy** — đừng để đến lúc bảo vệ mới thừa nhận.

**Phương án dự phòng:** nhờ sinh viên cùng lớp (vẫn là "ngoài nhóm"), ghi rõ số lượng thật và điều kiện trong báo cáo.

---

## 5. Kế hoạch cụ thể cho 9 ngày

| Ngày | Việc | Nguồn |
|---|---|---|
| 1 | Tải VIVOS, trích 10 người → 10 clip 15s | HuggingFace |
| 1 | Ghi âm 3 bạn trong nhóm → 3 clip 15s | Tự thu |
| 2 | Cắt mỗi clip thành 3/5/10/15s → **52 clip** | Từ 13 clip gốc |
| 2 | Sinh 300 câu test phủ 6 thanh | Script tự viết |
| 3 | Chạy inference, xuất toàn bộ audio kết quả | Kaggle |
| 4–5 | Tổ chức chấm MOS (10 người) | Google Form |
| 6–7 | Tính similarity + WER, làm bảng lỗi theo thanh | Script |
| 8–9 | Viết báo cáo | — |

---

## 6. Bảng tổng hợp giấy phép

| Nguồn | Giấy phép | Dùng đồ án trường | Ghi chú |
|---|---|---|---|
| **VIVOS** | CC BY-NC-SA 4.0 | ✅ Được | Phi thương mại — đúng mục đích |
| **Common Voice** | CC0 1.0 | ✅ Được | Thoáng nhất |
| **FLEURS (vi)** | CC BY 4.0 | ✅ Được | Ít dữ liệu hơn |
| **Tự thu** | Của bạn | ✅ Được | Cần giấy đồng ý của người được ghi |
| **OmniVoice — mã nguồn** | Apache-2.0 | ✅ Được | `github.com/k2-fsa/OmniVoice` |
| **OmniVoice — bộ mã hoá âm thanh** | Boson Higgs Audio 2 Community License | ✅ Được, **phải kèm nguyên văn** | Ghi rõ: *Built with Higgs Materials licensed from Boson AI USA, Inc.* |
| viVoice | unknown | ⚠️ Tránh | 1000h nhưng giấy phép không rõ |
| viet-tts-dataset | research-only | ⚠️ Tránh làm clip mẫu | Audio là giọng máy |
| VLSP 2020/2021 | research-only | 🟡 Được nhưng mất thời gian | Phải đăng ký |

---

## 7. Ba việc bạn cần quyết

1. **Dùng VIVOS hay tự thu?** Mình khuyên **cả hai** (10 VIVOS + 3 tự thu).
2. **Có cần mình viết script sinh 300 câu không?** Mình có thể tạo bộ 300 câu phủ đủ 6 thanh ngay bây giờ, kèm script kiểm tra độ phủ.
3. **MOS: bạn xoay được 10 người ngoài nhóm không?** Nếu không, ta cần điều chỉnh chỉ tiêu trong phiếu **trước khi gửi thầy**.

---

*Nguồn tham khảo: VIVOS — AILAB, VNUHCM (2016), DOI 10.5281/zenodo.7068130 · Danh mục tổng hợp: github.com/lienlt10/awesome-vietnamese-speech-datasets*
