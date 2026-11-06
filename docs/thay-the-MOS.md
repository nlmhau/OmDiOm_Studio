# Thay thế phần C (MOS) bằng bộ đo khách quan

*Ngày 24/10/2026 · Dựa trên phân tích 4 file bạn vừa gửi*

---

## Trả lời trực tiếp

**Có, bỏ MOS được.** Nhưng phải thay bằng thứ **khách quan hơn**, không phải bằng cảm nhận.

Câu "âm thanh rất chuẩn, đạt 90/100" — mình tin là bạn đánh giá đúng. Nhưng vấn đề không nằm ở việc nó hay hay dở:

> **"90/100" là con số không đo được.** 90 trên thang nào? Ai đặt ra? Chấm mấy mẫu? Có ai ngoài nhóm xác nhận?

Và đây chính xác là điều thầy đã viết trong phiếu mẫu:

> *"Nhãn cần có quy trình xác định độc lập; nhãn sinh từ cảm nhận của chính người viết chỉ chứng minh khả năng học lại khẩu vị của nhóm."*

Nếu bạn nộp báo cáo với câu "nghe rất chuẩn, 90/100" — đó là **rơi đúng vào cái bẫy thầy đã cảnh báo**.

Nhưng có một lối ra tốt hơn MOS, và nó **mạnh hơn** MOS.

---

## 1. Phân tích 4 file bạn gửi — số liệu thật

### 1.1. Bộ 300 câu: **tốt hơn mình kỳ vọng**

| Kiểm tra | Kết quả | Đánh giá |
|---|---|---|
| Đúng 300 câu | 300 | ✅ |
| Phân bố 6 thanh | **50 / 50 / 50 / 50 / 50 / 50** | ✅ Hoàn hảo |
| Trùng lặp nguyên văn | **0 câu** | ✅ |
| Thanh nhãn là thanh **trội** trong câu | **295/300 = 98%** | ✅ Rất tốt |
| Có cột `speaker_id` để trống | Có | ✅ Đúng thiết kế corpus văn bản độc lập |
| Độ dài | 16–46 ký tự, TB 28,3 | ✅ Vừa phải |

**5 câu chưa đạt** (đều thuộc nhóm `nga`):

| ID | Nhãn | Thanh trội thực tế | Câu |
|---|---|---|---|
| S0231 | nga | **nặng** | Những kỷ niệm đẹp vẫn ở lại. |
| S0246 | nga | **sắc** | Bỗng thấy những bóng dáng quen thuộc. |
| S0247 | nga | **sắc** | Bỗng thấy những bóng dáng mờ ảo. |
| S0249 | nga | **sắc** | Bỗng thấy những bóng dáng trở lại. |
| S0250 | nga | **sắc** | Bỗng thấy những bóng dáng ở đó. |

→ Sửa 5 câu này là bộ dữ liệu **sạch 100%**. Việc nhỏ, nên làm.

### 1.2. Điểm yếu cần biết: đa dạng từ vựng thấp

| Chỉ số | Giá trị |
|---|---|
| Tổng âm tiết | 2.001 |
| Âm tiết độc nhất | **317** |
| Tỉ lệ đa dạng (TTR) | **0,158** |

Nguyên nhân rõ ràng khi nhìn mẫu:

```
Ba ra sân sau ngắm hoa.
Nam ra sân sau ngắm hoa.
Lan ra sân sau ngắm hoa.
An ra sân sau ngắm hoa.
```

Đây là **thiết kế có chủ đích** (template + đổi 1 từ) — và với bài kiểm tra thanh điệu thì **đúng**: cấu trúc câu cố định giúp cô lập biến thanh điệu.

Nhưng phải viết đúng trong báo cáo: *"bộ câu được thiết kế theo template nhằm cô lập biến thanh điệu, không nhằm đo độ tổng quát hoá từ vựng."* Nếu không nói trước, hội đồng sẽ hỏi "sao 300 câu mà chỉ có 317 âm tiết khác nhau".

---

## 2. ⚠️ Vấn đề nghiêm trọng nhất phải sửa ngay

File `BAO_CAO_KIEM_THU_6_THANH.txt` có tiêu đề:

> **"BÁO CÁO KIỂM THỬ OMNIVOICE — 300 CÂU / 6 THANH / 7 GIỌNG"**

Nhưng trong chính file đó ghi:

> *"Mỗi WAV thử có 8 câu"*

### Sự thật từ số liệu

| | |
|---|---|
| Số câu trong corpus | 300 |
| Số câu **thực sự được sinh** | **8** |
| Số lượt sinh | 7 giọng × 8 câu = **56** |
| Tổng audio tạo ra | **107,66 giây** |
| Nếu đúng 300 câu | phải là ~**4.000 giây** |

**300 câu chưa từng được đưa qua model.** Chỉ 8 câu được sinh, lặp lại trên 7 giọng.

Nếu bạn nộp báo cáo với tiêu đề "kiểm thử 300 câu", đó là **sai lệch số liệu** — và đây là loại sai lệch dễ bị phát hiện nhất khi bảo vệ: chỉ cần mở file WAV ra đếm là thấy 8 câu.

### Tin tốt: chạy đủ 300 câu chỉ mất ~7 phút GPU

| | |
|---|---|
| 300 câu × 7 giọng | 2.100 lượt sinh |
| Thời lượng audio | ~67 phút |
| Thời gian sinh (RTF ≈ 0,1 trên T4) | **~7 phút** |
| Thời gian thêm (đọc/ghi file) | ~3 phút |

Đây là **việc quan trọng nhất bạn nên làm hôm nay**. Không có nó, phần "300 câu" trong phiếu đề tài là chưa được chứng minh.

### Một lỗi nhỏ khác

Bảng `KET_QUA_7_GIONG.csv` có cột `duration_ok_12_to_20s` — giọng **KE đạt 11,39s**, dưới ngưỡng. Tự bạn đã gắn nhãn `False`. Nên sửa: hoặc thêm câu cho đủ 12s, hoặc dùng ngưỡng rộng hơn (10–20s) và ghi rõ lý do.

---

## 3. Bộ thay thế MOS: 4 chỉ số khách quan

Đây là câu trả lời cho câu hỏi của bạn. Thay vì 10 người ngồi nghe và chấm 1–5, ta đo bằng máy — **chạy lại được, không phụ thuộc khẩu vị, và chặt hơn MOS**.

| # | Chỉ số | Đo cái gì | Công cụ | Thay thế MOS ở điểm nào |
|---|---|---|---|---|
| **1** | **WER / CER** | Sinh audio → cho ASR đọc lại → so với câu gốc | PhoWhisper / faster-whisper | Đo **độ rõ chữ** — thứ MOS hỏi "nghe có hiểu không" |
| **2** | **Độ chính xác thanh điệu** | Trích đường F0 từng âm tiết → phân loại 6 thanh → ma trận nhầm lẫn | librosa `pyin` | Đo **đúng dấu** — đặc thù tiếng Việt, MOS không tách được |
| **3** | **Speaker similarity (SECS)** | Cosine giữa embedding giọng gốc và giọng clone | ECAPA-TDNN | Đo **độ giống giọng** — MOS hỏi "có giống người mẫu không" |
| **4** | **UTMOS** | MOS dự đoán bằng mạng neural, không cần người | `omnivoice/eval/mos/utmos.py` (repo đã có) | Thay **MOS tự nhiên** — nhưng là model, không phải cảm nhận |

### Vì sao bộ này tốt hơn MOS cho đồ án của bạn

| | MOS 10 người | Bộ 4 chỉ số |
|---|---|---|
| Chạy lại được | ❌ Kết quả đổi theo người chấm | ✅ Cùng input → cùng output |
| Thời gian | 10 người × 20 phút = **3,3 giờ người** | **~30 phút máy** |
| Phụ thuộc khẩu vị nhóm | ❌ Có | ✅ Không |
| Tách được lỗi thanh điệu | ❌ Không | ✅ **Có** (chỉ số 2) |
| So sánh giữa 7 giọng | Khó | ✅ Dễ |
| Trả lời được "tại sao sai" | ❌ | ✅ Chỉ đúng âm tiết nào sai |

**Điểm mấu chốt:** MOS cho bạn một con số. Bộ này cho bạn **biết sai ở đâu** — và đó là thứ hội đồng muốn nghe.

### Chỉ số 2 là đóng góp riêng của đồ án

Không có dataset nào trên mạng có "đo độ chính xác thanh điệu tiếng Việt của TTS". Nếu bạn làm được cái này, đó là **đóng góp gốc** — không phải chạy lại bài của người khác.

Cách làm: mỗi âm tiết tiếng Việt mang đúng 1 thanh. Trích F0 → phân loại 6 dạng đường:

| Thanh | Dạng đường F0 | Đặc trưng |
|---|---|---|
| ngang | phẳng, cao vừa | độ dốc ≈ 0 |
| huyền | giảm đều | slope < 0, kết thúc thấp |
| sắc | tăng đều | slope > 0, kết thúc cao |
| hỏi | **xuống rồi lên** | có điểm cực tiểu ở giữa |
| ngã | tăng, có gãy (thanh hầu hoá) | tăng mạnh + nhiễu |
| nặng | ngắn, giảm mạnh | slope âm lớn, thời lượng ngắn |

Sau đó so nhãn dự phòng với nhãn thật → **ma trận nhầm lẫn 6×6**.

> ⚠️ **Điều kiện bắt buộc:** phải **hiệu chuẩn bộ phát hiện trên giọng người thật trước**. Nếu nó chỉ đạt 80% trên giọng người, thì kết quả 65% trên giọng máy phải được đọc là "kém hơn người 15 điểm", không phải "sai 35%". Đây là bước ai cũng bỏ qua — và là chỗ ăn điểm.

---

## 4. Có cần giữ chút gì của con người không?

**Nên giữ, nhưng rút xuống rất nhẹ.** Ba lựa chọn:

| Mức | Cách làm | Thời gian |
|---|---|---|
| **Tối thiểu** | 3 bạn trong nhóm nghe và **đếm số âm tiết nghe sai** trên 50 câu. Không chấm điểm 1–5 — chỉ đếm lỗi. | 20 phút |
| **Vừa** | Thêm 1 người ngoài nhóm nghe 20 câu dạng ABX (nghe 2 mẫu, chọn mẫu giống bản gốc hơn) | 30 phút |
| **Đầy đủ** | MOS 10 người như kế hoạch cũ | 3+ giờ |

**Khuyến nghị của mình: mức "tối thiểu" + bộ 4 chỉ số khách quan.**

Lý do: đếm lỗi là việc **khách quan hơn** chấm điểm 1–5 (có/không, không có "7 điểm hay 8 điểm"). Và bạn vẫn có dữ liệu người thật để đối chiếu chéo — nếu máy báo CER 3% mà người đếm ra 2 lỗi/50 câu thì hai bên khớp nhau, rất thuyết phục.

---

## 5. Kế hoạch cụ thể (3 ngày)

| Ngày | Việc | Kết quả |
|---|---|---|
| **1** | Sửa 5 câu lỗi trong bộ 300. Chạy sinh **đủ 300 × 7**. | 2.100 file WAV, ~67 phút audio |
| **2** | Chạy bộ 4 chỉ số khách quan | Bảng + biểu đồ |
| **3** | 3 bạn đếm lỗi trên 50 câu. Viết phần đánh giá vào báo cáo | Số liệu người ↔ máy khớp nhau |

Sinh 300 câu là việc **nặng nhất và cũng dễ nhất** — script đã sẵn. Chỉ cần sửa đường dẫn.

---

## 6. Sửa lại đoạn trong phiếu đề tài

Nếu bạn chọn phương án này, **phải sửa mục 4.4 của phiếu** trước khi gửi thầy:

**Cũ:**
> *"Đánh giá MOS bởi người nghe ngoài nhóm, độ tương đồng giọng nói (speaker similarity) và tỉ lệ lỗi từ (WER) qua ASR…"*

**Mới:**
> *"Đánh giá bằng bộ chỉ số khách quan: tỉ lệ lỗi ký tự (CER) qua ASR, độ chính xác thanh điệu bằng phân tích đường F0 với ma trận nhầm lẫn 6×6, độ tương đồng giọng nói (speaker similarity) và UTMOS; tách kết quả theo từng thanh điệu và theo giọng. Kiểm chứng chéo bằng việc đếm lỗi thủ công của nhóm trên 50 câu."*

Sửa như vậy vẫn **chặt hơn** bản cũ, và không còn yêu cầu 10 người nghe ngoài nhóm — thứ khó thực hiện nhất.

---

## 7. Ba điều mình không thể tự đánh giá

Nói rõ để bạn biết giới hạn của nhận xét này:

1. **Mình không nghe được audio.** Nên "90/100" mình không xác nhận được — chỉ nói được là nó chưa phải con số đo được.
2. **Mình không biết 7 giọng `.pt` lấy từ đâu.** Tên `tran_thy`, `u_linh`, `giong_nu_tre` là tên người. Nếu là giọng thật, báo cáo **phải có** mục nguồn gốc + đồng ý sử dụng. Đây là chỗ hội đồng hay hỏi về đạo đức AI.
3. **Chưa kiểm chứng được model có thật sự xử lý tốt tiếng Việt.** Bộ 4 chỉ số sẽ trả lời câu này bằng số.

---

*Script thực thi bộ 4 chỉ số: `eval/eval_objective.py`. Script sinh đủ 300 câu: `eval/synth_300.py`.*
