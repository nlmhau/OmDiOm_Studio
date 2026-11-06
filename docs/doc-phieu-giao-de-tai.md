# Đọc "Phiếu giao đề tài" — và nó áp dụng được gì

*Đọc ngày 24/10/2026 · Nộp báo cáo: **02/11/2026** → còn **9 ngày***

---

## 1. Trước hết: đây là một đề tài KHÁC

| | Đồ án đang làm | Phiếu giao đề tài |
|---|---|---|
| Môn | Chuyên đề TTNT | **Học sâu và ứng dụng** |
| Đề tài | Dựng lại VoiceStudio (TTS tiếng Việt) | **Phân loại phong cách lái xe từ UAH DriveSet** |
| Dữ liệu | Âm thanh | Cảm biến gia tốc + GPS |
| Model | OmniVoice (diffusion TTS) | Cây quyết định + MLP nhỏ |
| Đầu ra | Audio WAV | Nhãn trên trục thời gian |

**Không có gì chuyển được về kỹ thuật**: không model, không code, không dữ liệu, không thư viện. Nếu bạn định hỏi "lấy code TTS dùng cho bài này được không" — không.

Nhưng câu hỏi đáng hỏi hơn là: **phương pháp trong phiếu này có áp dụng cho đồ án TTS không?** Câu trả lời là **có, và nó tốt hơn cái mình đã đưa bạn.**

---

## 2. Phiếu này thực chất là một rubric chấm điểm

Đọc kỹ từng câu, bạn sẽ thấy giảng viên đang nói rõ **ông ấy sẽ chấm cái gì**. Đây là thông tin rất có giá:

| Câu trong phiếu | Ý thật của giảng viên | Áp dụng cho đồ án TTS |
|---|---|---|
| *"Nhãn cần có quy trình xác định độc lập; nhãn sinh từ ngưỡng gia tốc chỉ chứng minh khả năng học lại quy tắc đó"* | **Đừng dùng chính quy tắc của bạn để tạo nhãn rồi train model học lại quy tắc đó.** Đó là vòng tròn, không phải nghiên cứu. | ✅ **Rất đúng.** Đánh giá TTS bằng chính cảm nhận của người viết prompt là vòng tròn. Phải có MOS từ người ngoài. |
| *"Chia theo chuyến hoặc người lái TRƯỚC khi tạo cửa sổ chồng lấn"* | **Cảnh báo rò rỉ dữ liệu.** Chia sau khi tạo cửa sổ chồng lấn = cửa sổ trùng nằm cả train lẫn test. | ✅ Chia tập **trước khi** chọn câu test. Đừng test trên câu đã dùng làm clip mẫu. |
| *"Chuẩn hóa bằng tham số học từ train"* | Không được tính mean/std trên toàn bộ dữ liệu. | ✅ Nguyên tắc: **không tinh chỉnh tham số trên tập test.** |
| *"So sánh baseline lớp phổ biến, cây quyết định và MLP nhỏ"* | **Luôn phải có baseline tầm thường.** Nếu model không hơn baseline thì vô nghĩa. | ✅ So sánh `num_step` 8/16/32 với nhau — cái nào cũng phải có mốc so. Baseline = giọng mặc định không clone. |
| *"Dùng cùng tập kiểm tra"* | Công bằng khi so sánh. | ✅ Mọi thí nghiệm phải chạy trên cùng bộ câu. |
| *"Đánh giá macro F1, recall theo phong cách và theo người lái giữ lại"* | **Đo theo từng nhóm**, không chỉ 1 con số trung bình. | ✅ Đo **theo từng loại dấu thanh** (hỏi/ngã/nặng), không chỉ 1 điểm MOS chung. |
| *"Khảo sát độ dài cửa sổ"* | Phải làm **ablation** một siêu tham số then chốt. | ✅ Ta đã có: ablation `num_step`. |
| *"Nêu hạn chế khi gán nhãn cấp chuyến cho từng cửa sổ"* | Phải **nói thẳng điểm yếu của phương pháp mình dùng.** | ✅ Phải ghi rõ: model chưa huấn luyện riêng cho tiếng Việt. |
| *"Dùng gom cụm… không tự đồng nhất cụm với hành vi nguy hiểm"* | Không được **suy diễn quá xa** kết quả unsupervised. | ✅ Không được nói "giọng nghe tự nhiên" khi chưa có người chấm. |

### Kết luận phần này

Ba điều mình đã thiếu trong bản đặc tả trước:

1. **Baseline tầm thường** — mình chưa yêu cầu so với một mốc vô nghĩa để chứng minh model có giá trị.
2. **Đo theo từng nhóm** — mình chỉ có 1 con số MOS chung, chưa tách theo dấu thanh.
3. **Câu "nêu hạn chế" như một yêu cầu bắt buộc**, không phải phần phụ lục tuỳ chọn.

Nếu bạn áp ba điều này vào đồ án TTS, phần phương pháp sẽ chặt hơn hẳn. **Đây là giá trị thật của file PDF này** — không phải ở đề tài lái xe, mà ở cách giảng viên đặt câu hỏi.

---

## 3. Nếu bài lái xe là bài thật: ba cạm bẫy phải biết trước

Mình đã tra dữ liệu UAH-DriveSet. Đây là những gì phiếu **gợi ý** nhưng không nói hết.

### Dữ liệu thực tế gồm gì

| | |
|---|---|
| Nguồn | DriveSafe app (điện thoại), công bố 2016, ĐH Alabama–Huntsville |
| Người lái | **6 người** (5 nam, 1 nữ), 6 xe khác nhau |
| Phong cách | 3: normal · drowsy · aggressive |
| Tuyến | Motorway 25 km · Secondary 16 km |
| Tổng thời lượng | **~500 phút**, ~3,3 GB |
| Số chuyến | ~7 chuyến/người → **~42 chuyến** |
| Tần số | IMU (`RAW_ACCELEROMETERS.txt`) **10 Hz** · GPS (`RAW_GPS.txt`) **1 Hz** |
| Nhãn hiện có | **Từ tên thư mục chuyến**, ví dụ `...-AGGRESSIVE-MOTORWAY` |

### ⚠️ Cạm bẫy 1 — Nhãn cấp chuyến gán cho từng cửa sổ

Một chuyến "buồn ngủ" thực tế **phần lớn thời gian vẫn là lái bình thường**, chỉ có vài đoạn vi phạm. Nếu bạn gán mọi cửa sổ trong chuyến đó là `drowsy`, bạn đang dạy model một điều sai.

Hệ quả: **trần hiệu năng bị chặn bởi chất lượng nhãn, không phải bởi model.** Bạn có thể train hoàn hảo mà F1 vẫn thấp — và không phải lỗi của bạn.

**Cách xử lý để ghi vào báo cáo:**
- Báo cáo kết quả với nhãn cấp chuyến (trung thực với đề bài)
- Thêm **phân tích lỗi theo thời gian trong chuyến**: model đoán sai tập trung ở đầu/cuối chuyến hay rải đều?
- Nếu dự đoán sai rải đều → bằng chứng nhãn chuyến không đúng ở cấp cửa sổ. Đây là **phát hiện có giá trị**, không phải thất bại.

### ⚠️ Cạm bẫy 2 — Rò rỉ do cửa sổ chồng lấn

3.000 cửa sổ từ ~42 chuyến = **~70 cửa sổ mỗi chuyến**. Nếu cửa sổ chồng lấn 50% (bước nhảy = nửa độ dài) và bạn chia train/test **ngẫu nhiên**, hai cửa sổ gần như trùng nhau sẽ nằm ở cả hai phía → **F1 cao giả tạo, có thể 95%+**, và bạn sẽ tưởng mình giỏi.

Phiếu đã cảnh báo đúng thứ tự: **chia theo chuyến hoặc người lái TRƯỚC**, rồi mới tạo cửa sổ trong từng tập.

> Đây là lỗi phổ biến nhất trong các bài báo về UAH-DriveSet. Nếu bạn làm đúng, đó đã là điểm cộng.

### ⚠️ Cạm bẫy 3 — Chỉ 6 người lái

"Đánh giá recall theo người lái giữ lại" nghe hay, nhưng với **n=6** thì leave-one-driver-out chỉ có 6 fold, mỗi fold ~7 chuyến test. Kết quả sẽ **dao động rất mạnh** giữa các fold.

**Phải báo cáo trung bình ± độ lệch chuẩn qua 6 fold**, không báo một con số duy nhất. Và phải nói rõ: n=6 không đủ để kết luận về khả năng tổng quát hoá.

### ⚠️ Cạm bẫy 4 — Confounding theo tuyến đường

Mỗi người lái thực hiện mỗi phong cách trên **cùng một tuyến**. Nếu phân bố không cân bằng (ví dụ `drowsy` chỉ có trên secondary road), model sẽ **học tuyến đường chứ không học phong cách**.

**Việc phải làm ngay:** vẽ bảng chéo **nhãn × loại đường**. Nếu lệch nặng, phải nêu rõ trong phần hạn chế.

### ⚠️ Cạm bẫy 5 — Đừng dùng nhãn có sẵn của DriveSafe

Dataset có sẵn phần "processed semantic information" với tỷ lệ Normal/Drowsy/Aggressive do chính DriveSafe tính. **Nếu bạn lấy các con số đó làm nhãn rồi train model khác, bạn chỉ đang học lại DriveSafe.**

Đây chính xác là điều phiếu cảnh báo: *"nhãn sinh từ ngưỡng gia tốc chỉ chứng minh khả năng học lại quy tắc đó"*.

---

## 4. Nếu làm bài này trong 9 ngày

| Ngày | Việc |
|---|---|
| **1–2** | Tải dữ liệu, parse `RAW_ACCELEROMETERS` + `RAW_GPS`, đồng bộ thời gian 1 Hz → 10 Hz, kiểm missing. Vẽ bảng chéo nhãn × tuyến. |
| **3** | Tạo cửa sổ + đặc trưng thống kê. **Chia theo chuyến trước**, rồi mới cắt cửa sổ. |
| **4** | Baseline lớp phổ biến + cây quyết định. Bắt đầu thấy con số. |
| **5** | MLP nhỏ + chuẩn hoá. So sánh 3 mô hình trên cùng test. |
| **6** | Ablation độ dài cửa sổ (5s / 10s / 30s / 60s). |
| **7** | Leave-one-driver-out, báo cáo mean ± std. Phân tích lỗi. |
| **8** | Demo + confusion matrix + ví dụ dự đoán sai. |
| **9** | Viết báo cáo. |

Đây là lịch **rất chặt** — không có ngày dự phòng. Nếu dữ liệu tải chậm hoặc file lỗi, sẽ trượt.

---

## 5. Câu hỏi mình cần bạn xác nhận

Ba điều mình chưa rõ, và chúng đổi hẳn việc mình nên làm tiếp:

1. **Hai đề tài này có cùng tồn tại không?** Đồ án TTS cho môn "Chuyên đề TTNT", còn bài lái xe cho môn "Học sâu và ứng dụng"?
2. **Nếu chỉ chọn một** — cái nào là cái bạn thực sự phải nộp?
3. **Bạn muốn mình làm gì với bài lái xe?** Dựng pipeline, viết báo cáo, hay chỉ cần khung phân tích như file này?

Mình không muốn tự đoán rồi dựng sai thứ bạn cần — nhất là khi chỉ còn 9 ngày.

---

*Nguồn dữ liệu UAH-DriveSet: Romera et al., "Need Data for Driver Behaviour Analysis? Presenting the Public UAH-DriveSet", IEEE ITSC 2016. Tải tại robesafe.uah.es — file `UAH-DRIVESET-v1.zip`.*
