# PHỤ LỤC E — PHIẾU ĐỒNG Ý SỬ DỤNG GIỌNG (điền bù)

> Dùng khi **đã thu âm rồi** và cần ghi lại bằng chứng. Đây là việc *ghi chép lại sự thật đã xảy
> ra*, không phải xin phép sau. Điền đúng những gì đã xảy ra; chỗ nào không nhớ thì ghi `khong_ro`.

---

## 1. Vì sao cần tệp này (30 giây)

Hội đồng và người chấm hỏi đúng một câu: *"7 giọng này của ai, thu khi nào, họ có đồng ý không?"*
`DECISIONS.md` đánh dấu đây là giả định **G1** (27/10: đã đóng một phần, **mức C**). Một tờ giấy 7 dòng biến
"không rõ nguồn gốc" thành "có truy vết", và không tốn thêm phút thu âm nào.

Chi phí: **10 phút**. Giá trị: giữ được 7 giọng bạn đã làm.

---

## 2. Bảng điền (chép vào `data/REF/DONG_Y_7_GIONG.md`)

| # | Mã giọng | Tệp .pt | Người đọc (tên hoặc viết tắt) | Ngày thu (ước lượng) | Thiết bị | Đồng ý | Ghi chú |
|---|---|---|---|---|---|---|---|
| 1 | U_LINH | `u_linh.pt` | | | | ☐ bằng lời ☐ bằng văn bản | |
| 2 | ONG_GIA | `giong_ong_gia.pt` | | | | ☐ bằng lời ☐ bằng văn bản | |
| 3 | KE | `ke.pt` | | | | ☐ bằng lời ☐ bằng văn bản | |
| 4 | TRAN_THY | `tran_thy.pt` | | | | ☐ bằng lời ☐ bằng văn bản | |
| 5 | NU_TRE | `giong_nu_tre.pt` | | | | ☐ bằng lời ☐ bằng văn bản | |
| 6 | TRAI_TRE | `giong_trai_tre.pt` | | | | ☐ bằng lời ☐ bằng văn bản | |
| 7 | TRE_EM | `giong_tre_em.pt` | | | | ☐ bằng lời ☐ bằng văn bản | |

**Ba mức đồng ý — ghi đúng mức thật, đừng nâng lên:**

| Mức | Nghĩa | Được dùng cho |
|---|---|---|
| **A** — văn bản có chữ ký | người đọc đã ký phiếu | mọi thứ trong đồ án, kể cả trình diễn trước hội đồng |
| **B** — bằng lời, có ghi âm/người làm chứng | họ nói "được" và có bằng chứng | mọi thứ trong đồ án |
| **C** — chỉ là thành viên nhóm tự đọc | họ là người trong nhóm | mọi thứ trong đồ án, ghi rõ "thành viên nhóm" |
| **X** — không liên hệ lại được | mất liên lạc | **chỉ dùng nội bộ để thí nghiệm**, ghi rõ trong báo cáo, không phát hành, không trình diễn công khai |

> Trường hợp **C** rất phổ biến và hoàn toàn hợp lệ — 7 giọng có thể là 7 thành viên/người quen
> trong nhóm. Chỉ cần ghi đúng là "thành viên nhóm tự đọc".
> Trường hợp **X** không phải thảm hoạ: vẫn dùng được, chỉ thêm một dòng trung thực trong báo cáo.

---

## 3. Mẫu câu xác nhận (nếu xin được chữ ký)

> Tôi, ................, đồng ý cho nhóm thực hiện đồ án *"Nghiên cứu và ứng dụng mô hình học sâu
> trong tổng hợp, nhân bản giọng nói tiếng Việt zero-shot"* sử dụng bản ghi âm giọng của tôi
> (thu ngày ..../..../2026) để **nghiên cứu và đánh giá trong khuôn khổ đồ án môn học**.
> Tôi hiểu rằng bản ghi và các bản tổng hợp từ giọng tôi **không được phát hành công khai, không
> dùng cho mục đích thương mại, không dùng để giả mạo**. Tôi có thể yêu cầu xoá bất cứ lúc nào.
>
> Ký / ghi rõ họ tên: ................  Ngày: ..../..../2026

Phiếu này không cần công chứng. Một ảnh chụp tờ giấy viết tay có chữ ký là đủ.

---

## 3b. Ai được ký — luật cứng

> **Đồng ý phải đến từ CHÍNH NGƯỜI ĐỌC, không phải từ chủ dự án.**

| Tình huống | Hợp lệ? |
|---|---|
| Người đọc tự ghi tên mình vào cột "Người đọc" | ✅ |
| Trưởng nhóm nói "cả nhóm đồng ý" và tự điền 7 dòng | ⚠ **chỉ hợp lệ nếu cả 7 là thành viên nhóm** (mức C) — và cột "Người đọc" phải ghi **tên từng người** |
| Agent/AI tự điền `✅ co` cho 7 dòng vì người dùng nói "đồng ý đi" | ❌ **KHÔNG hợp lệ.** Đây là chữ ký của người khác |
| Người đọc không còn liên lạc | Ghi mức **X**, vẫn dùng nội bộ, ghi rõ trong báo cáo |

Cột **"Người đọc"** phải là tên người thật (hoặc viết tắt đủ nhận diện), **không** được là
`người dùng`, `agent`, `nhóm`, `admin`, hay để trống.

Nếu 7 giọng không phải thành viên nhóm mà là người ngoài, thì mỗi người cần một dòng xác nhận của
chính họ (tin nhắn, ảnh chụp phiếu, hoặc ghi âm câu "tôi đồng ý"). Không có thì ghi mức **X**.

---

## 3c. Giả định G1 chỉ đóng được khi có đủ hai thứ

`DECISIONS.md` ghi G1 = *"7 file `.pt` là giọng thật hợp lệ do nhóm tự tạo"* — **chưa kiểm chứng**.
Chỉ được đổi thành *đã kiểm chứng* khi:

1. `data/REF/DONG_Y_7_GIONG.md` có **7 dòng, cột "Người đọc" ghi tên thật của từng người**;
2. mỗi dòng có mức đồng ý **A, B hoặc C** (không phải X).

Nếu còn dòng mức X, G1 giữ nguyên trạng thái **một phần** và báo cáo phải ghi rõ.

Agent **không được** tự sửa `DECISIONS.md` để đóng G1. Việc đó chỉ xảy ra khi người dùng xác nhận
từng dòng.

---

## 3d. Bản điền sẵn cho trường hợp "thành viên nhóm tự đọc"

Người dùng đã xác nhận 7 giọng là **thành viên nhóm / người quen tự đọc** → mức **C**.
Chỉ cần điền cột "Người đọc" bằng tên thật. Chép bảng dưới vào `data/REF/DONG_Y_7_GIONG.md`
rồi thay `<tên>` — **không** để nguyên `<tên>`, **không** ghi "người dùng", "nhóm", "agent".

```markdown
| # | Mã giọng | Tệp .pt | Người đọc | Ngày thu | Thiết bị | Đồng ý | Ghi chú |
|---|---|---|---|---|---|---|---|
| 1 | U_LINH | `u_linh.pt` | <tên> | <ngày> | <thiết bị> | C | thành viên nhóm tự đọc |
| 2 | ONG_GIA | `giong_ong_gia.pt` | <tên> | <ngày> | <thiết bị> | C | thành viên nhóm tự đọc |
| 3 | KE | `ke.pt` | <tên> | <ngày> | <thiết bị> | C | thành viên nhóm tự đọc |
| 4 | TRAN_THY | `tran_thy.pt` | <tên> | <ngày> | <thiết bị> | C | thành viên nhóm tự đọc |
| 5 | NU_TRE | `giong_nu_tre.pt` | <tên> | <ngày> | <thiết bị> | C | thành viên nhóm tự đọc |
| 6 | TRAI_TRE | `giong_trai_tre.pt` | <tên> | <ngày> | <thiết bị> | C | thành viên nhóm tự đọc |
| 7 | TRE_EM | `giong_tre_em.pt` | <tên> | <ngày> | <thiết bị> | C | thành viên nhóm tự đọc |
```

**Trạng thái 27/10:** người dùng xác nhận **đã tự tay điền 7 tên người đọc** (thành viên nhóm /
người quen tự đọc), mức **C**. G1 = *đã kiểm chứng một phần*. Kiểm lại bằng:
`python tools/du_lieu/kiem_du_lieu.py --bo v1` → phải thấy `G8.6 OK` **và** `G8.7 OK`.
Nếu `G8.7` còn vàng thì cột "Đồng ý" chưa ghi `C` — điền nốt, đừng coi là xong.

---

## 4. Nếu không điền được đủ 7 dòng

Không cần bịa. Ba lựa chọn, theo thứ tự tốt dần:

1. **Điền những gì biết** — kể cả chỉ ghi "thành viên nhóm: Minh Hậu". Đủ để dùng.
2. **Đánh dấu X cho người mất liên lạc** — vẫn dùng, thêm một dòng vào báo cáo.
3. **Bổ sung bằng VIVOS** — nếu thiếu hẳn một giọng, cắt từ VIVOS với **mã người nói thật**
   (`VIVOSSPK01`…), không đặt tên giả. Dùng chung một bộ dữ liệu là hợp lệ về giấy phép.

Việc **không** được làm: ghi "đã có đồng ý" khi chưa có. Một dòng trung thực đáng giá hơn bảy
dòng đẹp.

---

## 5. Ghi vào báo cáo thế nào

Câu mẫu cho mục "Nguồn dữ liệu & giấy phép":

> Bảy giọng tham chiếu được thu từ bảy người nói, ghi bằng `VoiceClonePrompt` của OmniVoice
> (`omnivoice==0.2.1`), lưu ở định dạng `.pt`. Danh sách người đọc, ngày thu, thiết bị và mức
> đồng ý ghi trong `data/REF/DONG_Y_7_GIONG.md`. Bản ghi âm gốc **không** được phát hành;
> bản tổng hợp chỉ dùng trong phạm vi đồ án.

Nếu có giọng mức X:

> Giọng `XXX` chưa liên hệ lại được để xác nhận bằng văn bản; giọng này chỉ dùng cho thí nghiệm
> nội bộ, không xuất hiện trong tài liệu trình diễn.

Câu đó không làm yếu đồ án. Nó làm đồ án **đáng tin**.
