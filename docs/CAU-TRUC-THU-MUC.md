# Cấu trúc thư mục — chuẩn cho dự án này

> Đọc xong tệp này anh biết: thư mục nào giữ nguyên, tệp mới đặt ở đâu, thứ gì
> không được mang vào repo, và cách kiểm bằng một lệnh.

---

## 1. Trạng thái đo được

| Đo | Số | Nghĩa |
|---|---|---|
| Mục ở gốc | **17** | 12 thư mục + 5 tệp lẻ + `.gitignore` |
| Tổng số tệp | **45** | trong đó 39 tệp nằm trong thư mục |
| Kích thước | **1,1 MB** | mức trần là 100 MB |
| Tệp lẻ ở gốc | **6** | `README.md` `MO_TA_DU_AN.md` `DECISIONS.md` `requirements.txt` `.gitignore` `chay_local.bat` |
| Tham chiếu chéo | **~90** | `tools/` bị 17 tệp trỏ tới · `kaggle/` 11 · `server/` 10 · `eval/` 9 · `voices/` `qc/` 8 · `ui/` `docs/` 7 |

Bản trước khi dọn: **81 tệp · 5,1 MB**. Đã bỏ 36 tệp — toàn bộ là tài liệu điều
hành nội bộ, lịch sử notebook, và tệp chỉ để công cụ AI đọc (xem §10). Không
tệp nào trong số đó là thứ máy cần để chạy.

Trên máy anh, trước khi chép vào:

```
D:\OmDiOm\
├─ UI\        index.html (bản cũ)
└─ voices\    7 tệp .pt
```

Đây **không phải repo** — chỉ là hai thư mục rời. Không có `server/` thì giao
diện không gọi được giọng nào; không có `manifest.json` thì không ai biết tệp
`.pt` nào là của ai.

---

## 2. Sáu nguyên tắc

1. **Một thư mục — một việc.** Tên thư mục trả lời "bên trong là gì", không
   phải "làm hồi nào". `notebook/` là một việc; `pha-2-cu/` không phải.
2. **Gốc chỉ để điều hướng.** Ở gốc chỉ có tệp dẫn đường + các thư mục. Tệp lẻ
   chỉ được thêm nếu là một trong sáu tên ở §1. Muốn thêm tên thứ bảy thì phải
   sửa `tools/cau_truc.py` — đó là chủ ý, để tệp lạ không lọt vào.
3. **Đừng di chuyển thứ đang được trỏ tới.** Mỗi lần đổi đường dẫn là một lần
   link chết âm thầm. §1 cho thấy gần như mọi thư mục đều đang được trỏ tới;
   di chuyển phải làm trọn một lần bằng script, không sửa tay.
4. **Dữ liệu và mã không ở chung.** `.wav`, `.pt`, `.csv` không nằm cạnh `.py`.
   Dữ liệu nguồn ở `CAU/`, giọng ở `voices/`, kết quả chạy ở `ket_qua/`.
5. **Một cửa vào: `README.md`.** Tài liệu không được README trỏ tới thì hoặc
   xoá, hoặc thêm vào README. Không có cửa thứ ba.
6. **Không mang thứ sinh lại được.** `.pt` sinh từ clip gốc, WAV sinh từ
   notebook, `__pycache__` sinh từ Python. Chỉ giữ thứ không sinh lại được:
   mã nguồn, câu, quyết định, số liệu đo.

---

## 3. Cây thật (45 tệp)

```
D:\OmDiOm\
├─ README.md                ← cửa vào duy nhất: đọc là chạy được
├─ MO_TA_DU_AN.md           ← dự án là gì, đang ở đâu, thiếu gì
├─ DECISIONS.md             ← 4 quyết định gốc + lý do (kim chỉ nam khi sửa)
├─ requirements.txt         ← ghim phiên bản
├─ .gitignore               ← chặn .pt, WAV, __pycache__
├─ chay_local.bat           ← chạy thử trên máy, không cần GPU
│
├─ server\                  ← chương trình chạy           (3 tệp)
│   ├─ app.py               FastAPI: 5 endpoint + 3 endpoint giọng
│   ├─ engine.py            bọc OmniVoice, nạp model, sinh âm thanh
│   └─ voices.py            thư viện giọng: quét, lưu, xoá
│
├─ ui\                      ← giao diện                    (1 tệp)
│   └─ index.html           5 tab · CSS nhúng · không phụ thuộc ngoài
│
├─ voices\                  ← thư viện giọng               (2 tệp)
│   ├─ manifest.json        danh mục — commit được, KHÔNG chứa giọng
│   ├─ README.md            quy ước đặt tên
│   └─ *.pt                 ← anh tự chép 7 tệp vào đây, không đi kèm gói
│
├─ kaggle\                  ← thứ chạy trên GPU Kaggle     (1 tệp)
│   └─ OmDiOm.ipynb         21 ô · tự chứa · T4 × 2
│
├─ CAU\                     ← dữ liệu NGUỒN                (2 tệp)
│   └─ 300_CAU_6_THANH_VIET.csv / .json
│
├─ tools\                   ← script chạy tay             (12 tệp)
│   ├─ cau_truc.py          cổng kiểm cấu trúc, C1–C7
│   ├─ kiem_goi.py          cổng kiểm gói, K1–K7
│   └─ *.py                 10 script thu thập / làm sạch / kiểm Pha A
│
├─ eval\                    ← đo chất lượng                (4 tệp)
├─ qc\                      ← kiểm phiếu, số liệu          (2 tệp)
├─ docs\                    ← tài liệu người đọc           (8 tệp)
│   ├─ chuc-nang.html       "tệp chức năng"
│   ├─ CAU-TRUC-THU-MUC.md  ← tệp này
│   ├─ bao-cao.md           khung báo cáo
│   └─ …                    nguồn dữ liệu · thay thế MOS · phiếu đồng ý giọng
├─ notebook\                ← notebook v5 + nhận xét        (2 tệp)
├─ phieu\                   ← biểu mẫu giao đề tài         (1 tệp)
└─ phan-tich\               ← phân tích phiếu duyệt         (1 tệp)
```

Không có `data/`, `ket_qua/`, `src/`, `tests/` — chúng chưa cần. Thư mục chỉ
được tạo khi có tệp thật sắp đặt vào (§4 ghi rõ đặt ở đâu).

---

## 4. Tệp mới nên đặt ở đâu

| Tạo ra cái gì | Đặt ở | Ghi chú |
|---|---|---|
| Endpoint, lớp xử lý model | `server/` | tên `snake_case.py` |
| Giao diện | `ui/index.html` | |
| Giọng `.pt` | `voices/` | tên giữ dấu: `Linh_Đức_Tú.pt` |
| Câu để đọc | `CAU/` | dữ liệu nguồn, giữ nguyên không sửa |
| Dữ liệu sau khi lọc | `data/vN/` | tạo khi có, **không** commit |
| WAV sinh ra khi chạy | `ket_qua/` | **không** để cạnh mã, **không** commit |
| Notebook chạy trên Kaggle | `kaggle/` | |
| Script chạy một lần | `tools/` | |
| Tài liệu cho người đọc | `docs/` | |
| Biểu mẫu, phiếu | `phieu/` | |
| Số liệu đo, đối chiếu | `eval/` hoặc `qc/` | |
| Nhật ký nội bộ, kế hoạch | **không mang vào repo** | xem §10 |

---

## 5. Ba bước trên máy anh

```powershell
# 1. chép cả gói vào D:\OmDiOm
#    (giải nén ZIP vào D:\OmDiOm, gộp với thư mục UI\ và voices\ đang có)

# 2. chuyển 7 tệp giọng vào đúng chỗ
Move-Item "D:\OmDiOm\voices\*.pt" "D:\OmDiOm\OmDiOm\voices\"

# 3. kiểm
cd D:\OmDiOm\OmDiOm
python tools\cau_truc.py
python tools\kiem_goi.py
```

Sau bước 2, `D:\OmDiOm\OmDiOm\voices\` có 7 tệp `.pt` + `manifest.json` +
`README.md`. Máy chủ tự tìm thư mục này (`../voices` so với `server/`), nên
`OMNIVOICE_VOICES` không cần đặt gì.

Thư mục `D:\OmDiOm\UI\` cũ: lấy `index.html` mới trong `ui\`, chép đè, rồi
xoá — từ đó chỉ còn một bản giao diện duy nhất.

---

## 6. Ba pha dọn dẹp — và vì sao đã dừng

### Pha 1 — làm ngay, không phá gì ✅ xong

- `requirements.txt` — người mới mở repo biết cần gì
- `.gitignore` — `.pt`, WAV, `__pycache__` không bị commit
- `voices/` + `manifest.json` + `README.md`
- `server/voices.py`, `ui/` 5 tab
- `tools/cau_truc.py`, `tools/kiem_goi.py`

### Pha 2 — gộp thư mục ❌ **không làm**

| Gộp | Thành | Số chỗ phải sửa link |
|---|---|---|
| `eval/` + `qc/` | `tools/` | 17 |
| `phieu/` + `phan-tich/` | `docs/` | 6 |
| `notebook/` | `kaggle/` | 4 |

**Chi phí thật: 27 chỗ sửa.** Lợi ích: gốc gọn hơn 4 mục. Đánh đổi này không
đáng: mỗi chỗ sửa sai là một link chết mà không ai báo. Cấu trúc 17 mục đã đủ
gọn; thêm nữa là đổi tên cho đẹp, không phải để dễ dùng.

### Pha 3 — đã cắt tệp, không di chuyển

Đã xoá 36 tệp (§10). Không di chuyển `server/`, `ui/`, `CAU/`, `voices/` —
notebook và giao diện trỏ thẳng vào.

---

## 7. Cổng kiểm

```powershell
cd D:\OmDiOm\OmDiOm
python tools\cau_truc.py     # C1–C7: cấu trúc
python tools\kiem_goi.py     # K1–K7: gói có khớp không
```

**`cau_truc.py`** — C1 không đòi gốc rỗng; nó so với **danh sách điều hướng
được phép** (6 tên ở §1), để tệp lạ vừa xuất hiện là bị bắt. Có `✗` là thoát
mã 1, cắm được vào quy trình như các cổng `G1…G9`.

**`kiem_goi.py`** — K4 so **SHA-256 của mã nhúng trong notebook** với mã thật
trong `server/`. Sửa `engine.py` mà quên sinh lại notebook là K4 báo đỏ ngay.
Đây là cổng chống lỗi đắt giá nhất của dự án: notebook và `server/` lệch nhau
thì mọi kết quả đo đều vô nghĩa.

Tạo phần còn thiếu (không xoá, không di chuyển gì):

```powershell
python tools\cau_truc.py tao
python tools\cau_truc.py cay     # in cây để đối chiếu §3
```

---

## 8. Quy ước tên

| Loại | Quy ước | Ví dụ |
|---|---|---|
| Script Python | `snake_case.py` | `lam_sach.py`, `cau_truc.py` |
| Tài liệu người đọc | `CHU-HOA.md` hoặc `chu-thuong.md`, **có gạch nối** | `CAU-TRUC-THU-MUC.md` |
| Giọng `.pt` | `Ten_Nguoi.pt`, **giữ dấu** | `Linh_Đức_Tú.pt` |
| Thư mục | `snake_case/` hoặc `CHU-HOA/` cho dữ liệu | `voices/`, `CAU/` |

Bắt buộc với mọi tệp mã và tài liệu: **không dấu, không khoảng trắng**. Ngoại
lệ duy nhất là tệp `.pt` trong `voices/` — ở đó dấu tiếng Việt là tên hiển thị,
và `voices.py` tự bỏ dấu để tạo `id` (`Linh_Đức_Tú.pt` → `Linh_Duc_Tu`).

---

## 9. Vì sao không dùng `src/`, `tests/`, `build/`

Mẫu đó dành cho thư viện Python đóng gói (`pip install` được). Đồ án này là
**ứng dụng**, không phải thư viện: không có `setup.py`, không phát hành lên
PyPI, và `server/app.py` được nhúng base64 vào notebook chứ không import từ
package. Thêm `src/` chỉ làm đường dẫn dài thêm một tầng mà không giải quyết
việc gì.

Cái đáng bắt chước từ dự án lớn là: **tệp điều hướng ở gốc, quy ước tên, cổng
kiểm tự động, và một cửa vào** — bốn thứ đó đều đã có ở trên.

---

## 10. Đã cắt gì, và vì sao

Bản 81 tệp → 45 tệp. Nguyên tắc: **một tệp chỉ ở lại nếu nó còn việc để làm**
— để chạy, để bảo vệ, hoặc để người khác đọc hiểu.

| Nhóm đã bỏ | Tệp | Vì sao |
|---|---|---|
| Công cụ AI đọc | `AGENTS.md`, `GEMINI.md` | Chỉ Antigravity đọc; không phục vụ người đọc hay máy chạy |
| Điều hành nội bộ | `BRIEF.md`, `PLAN.md`, `DANH-MUC-DA-DON.md` | Trạng thái việc đã xong; thay bằng `MO_TA_DU_AN.md` + `DECISIONS.md` |
| Kế hoạch thi hành | `KE_HOACH/` (16 tệp) | Việc đã làm rồi. Giữ lại đúng một tệp còn dùng: `PHU_LUC_E` → `docs/PHIEU-DONG-Y-GIONG.md` |
| Lịch sử notebook | 3 bản `.ipynb` v2/v3/v4 | Bản v5 là bản dùng. Giữ nhận xét, bỏ bản chạy cũ |
| Nhật ký nội bộ | `DOI-CHIEU-SUA-LOI.md`, `QC-v3.md`, `NHAN-XET…` (bản cũ) | Nhật ký quá trình vá; kết quả đã nằm ở `NHAN-XET-KET-QUA-CHAY-v3.md` |
| Prompt tái dựng | `prompt/` (3 tệp) | Prompt là công cụ dựng, không phải sản phẩm |
| Trang thừa | `qc/XEM-TRUOC_PHIEU_DUYET.html` (2,3 MB) | Phiếu duyệt bản đã ký là bản chuẩn; trang xem trước 280 link chết |
| Ảnh không dùng | `ui/ANH_THIET_KE_GIONG.png` (1,1 MB) | Được tham chiếu **0 lần** trong `index.html` |
| Bản nháp tài liệu | `DAC-TA-CHUC-NANG-v2.docx`, `nhan-xet-giao-dien.html`, `TOP-10-TEN-DE-TAI.md`, `GHI-CHU-*.md` | Bản `.docx`/`.html` là bản chuẩn; bản nháp đã bị thay |
| Tiện ích lẻ | `kaggle/SUA_NHANH.py` | Bản vá tay; notebook đã có mã đúng |

**Ba tệp được cứu, không xoá:** `DECISIONS.md` (D1–D4 — căn cứ bảo vệ: vì sao
`num_step=16`, vì sao bỏ MOS), `MO_TA_DU_AN.md` (mô tả dự án — tệp mô tả mà anh
yêu cầu đứng đầu thứ tự), `nhận xét kết quả chạy v3` (số liệu thật của lần chạy
2.100 WAV).
