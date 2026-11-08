# Đánh giá website NAFLD Insight bản V3 — 07/11/2026

**Đối tượng kiểm tra:** `Web/NAFLD_Insight_V3/NAFLD_Insight_V3_Fix_20261103/KhoanLuanTotNghiep/` (dưới đây viết `W3/`), bản sửa theo [06_DANH_GIA_WEB_V2.md](06_DANH_GIA_WEB_V2.md). Thư mục trùng 101/101 tệp với `Web/NAFLD_Insight_V3.zip`. Sau khi kiểm vẫn trùng: không tệp nào của web bị đổi, không sinh `__pycache__`.

**So với v2:** 75 tệp giữ nguyên, 14 tệp sửa, 12 tệp thêm; 19 tệp bị bỏ đều là cache (`.pytest_cache`, `__pycache__`). Tệp sửa chính: `app/app.py`, `src/input_data.py`, `src/research_evidence.py`, `artifacts/manifest.json`, `artifacts/thresholds.json`, `.streamlit/config.toml`, `requirements.txt`.

**Nguồn gốc bản sửa:** `docs/FIX_V2_20261103.md` ghi bản được tạo ngày 03/11 trong một "môi trường tạo patch" khác (test báo scikit-learn 1.8.0), chưa chạy giao diện thật.

---

## 1. Kết luận

**Mô hình và số liệu đúng. V3 sửa được gần hết lỗi của v2 và chạy ổn trên máy này. Chưa nên đưa lên GitHub hay ghi "đã nghiệm thu" khi chưa sửa 2 việc bắt buộc (N1, N2).**

| Hạng mục | Đánh giá | Bằng chứng chính |
|---|---|---|
| Mô hình, tiền xử lý, ngưỡng | **Đạt** | 5 `.joblib` trùng MD5 mô hình tuần 7 và preprocessor gói v2; `weights.json`, `groups.json` không đổi; ngưỡng Fusion (b) 5 seed × 3 loại trùng `nguong_3_loai_dung.json`, ngưỡng F1 lệch `nguong_khoa.json` gốc ≤ 5,6e-17 |
| Tái lập VAL qua luồng web | **Đạt** | 1.004/1.004 người qua (v2: 995), lệch xác suất ≤ 3,33e-16, 0 đổi nhãn; 4.680/4.680 người TRAIN qua bước kiểm nhập |
| Kiểm tra dữ liệu nhập | **Đạt phần lớn** | Mọi ca sai trong Bảng A của v2 đã bị chặn hoặc xử lý đúng; còn hở ở số đo thấp bất thường và nhập theo inch (N3) |
| Độ ổn định giao diện | **Đạt** | AppTest 40/40 bước; trình duyệt 1280 px và 375 px; lỗi sập L1 và lỗi L7, L8 không còn |
| Xử lý lỗi tài nguyên | **Đạt** | 6/6 ca thiếu hoặc hỏng tệp: thông báo tiếng Việt, không traceback, không lộ đường dẫn |
| Nội dung nghiên cứu | **Đạt** | Bảng VAL–TEST, PPV/NPV, hiệu chuẩn khớp tệp kết quả đã lưu; câu chốt dùng "chưa có đủ bằng chứng thống kê" |
| Toàn vẹn cấu hình | **Đạt trên máy này; không đạt sau `git clone` trên Windows** | Đổi ngưỡng, trọng số hay nền giải thích đều bị chặn; nhưng clone qua Git (`core.autocrlf = true`) làm web từ chối dự đoán (N1) |
| Bộ test đi kèm | **Một phần** | 65 passed, 1 skipped; 2/3 test AppTest của web hỏng do viết sai API (N2) |

**Trả lời ngắn:** chạy demo từ thư mục hoặc zip hiện tại thì ổn. Muốn đẩy lên repo nhóm hoặc để người khác clone về thì phải sửa N1 trước. Muốn ghi "đã nghiệm thu" thì sửa N2 và chạy đủ 15 luồng có ảnh chụp.

---

## 2. Cách kiểm và giới hạn

**Môi trường:** Python 3.12.10 trong `.venv` của v1, không cài thêm. Phiên bản thư viện trùng đúng mốc ghim trong `requirements.txt` của V3 (Streamlit 1.66.1, scikit-learn 1.9.0, LightGBM 4.6.0, pandas 3.0.5, NumPy 2.5.2, SciPy 1.18.1, joblib 1.6.0), nhưng đây không phải lần cài mới. Web chạy từ đúng thư mục V3 tại cổng 8503 (cấu hình `nafld-web-v3` thêm vào `.claude/launch.json`), có `-B`.

**Dữ liệu:** ca giả lập A, B, C; VAL (suy luận) và TRAIN (chỉ qua bước kiểm nhập). Không suy luận TEST; số TEST được đối chiếu với tệp kết quả đã lưu của tuần 8–9.

| Phép kiểm | Kết quả | Tệp bằng chứng (`kiem_ke/web_v3_07-11-2026/`) |
|---|---|---|
| Zip so thư mục; V3 so v2 | 101/101 trùng; 14 sửa, 12 thêm | `ket_qua/b0_so_zip_va_v2.txt` |
| Artifact, ngưỡng, nguồn của tệp mới | Xem mục 1 và 3 | `ket_qua/b1.txt` |
| 1.004 VAL qua luồng web; TRAIN qua kiểm nhập | Xem mục 1 | `ket_qua/b2.txt` |
| Giá trị biên, sai đơn vị, thiếu dữ liệu, CSV | Xem L2, L3, N3, N4 | `ket_qua/b3.txt`, `b7.txt` |
| Can thiệp trên bản sao; clone Git thật | Xem L5, N1 | `ket_qua/b4.txt`, `b4b_thu_sua_gitattributes.txt` |
| AppTest 40 bước (script viết lại, gọi API đúng) | 40 PASS | `ket_qua/b5.txt` |
| Thiếu hoặc hỏng tài nguyên | 6/6 thông báo thân thiện | `ket_qua/b6.txt` |
| Bộ test của web | 65 passed, 1 skipped; AppTest 2 failed, 1 passed | `ket_qua/c1_pytest_bo_test_cua_web.txt`, `c2_pytest_apptest_cua_web.txt` |
| Trình duyệt 1280 px và 375 px | Xem mục 3 | `anh/` (11 ảnh) |

Mã kiểm ở `ma_kiem/`. Mọi thao tác sửa tệp (đổi ngưỡng, xóa tài nguyên, clone Git) làm trên bản sao trong thư mục tạm, không làm trên V3.

**Chưa kiểm:** cài mới từ `requirements.txt` trên máy khác; clone trên Linux hoặc macOS; trình duyệt khác; chọn tệp CSV bằng hộp thoại thật (đã gán tệp bằng JavaScript); bấm "Tải CSV mẫu" và "Xuất bảng kết quả CSV" trên trình duyệt; nhiều người dùng cùng lúc; trình đọc màn hình; đánh giá lâm sàng.

---

## 3. Trạng thái 20 lỗi của bản v2

| Mã | Trạng thái V3 | Bằng chứng, ghi chú |
|---|---|---|
| L1 Sập khi xem dòng CSV | **Đã sửa** | Trình duyệt: có kết quả nhập tay → CSV → "Hiển thị giải thích cho dòng này" → hiện 59,49%, giải thích chạy (`anh/04`, `05`); AppTest U10 |
| L2 Nhận giá trị phi lý | **Đã sửa phần lớn** | Chặn: eo 1,12, 0, 11200; BMI 0, 345, 5000; HA 80/140; HbA1c 61; TG 1,200; ngồi 2000. Còn N3 |
| L3 Nhập mmol/L | **Sửa một phần** | Có cảnh báo và ghi rõ mg/dL, nhưng vẫn ra kết quả (ca A với 4 xét nghiệm theo mmol/L: 43,66%, kèm 9 cảnh báo). Biên bản sửa đã nêu giới hạn này |
| L4 Không có TEST | **Đã sửa** | Bảng VAL–TEST 5 mô hình, hình tuần 9, câu chốt đúng; số trùng `KetQua_Tuan9/bang/val_vs_test.csv` (`anh/08`) |
| L5 Khẳng định SHA-256 sai | **Đã sửa trên máy** | Đổi ngưỡng, trọng số hoặc 1 ô nền giải thích → web từ chối. Xem thêm N1 |
| L6 Thiếu định nghĩa nhãn | **Đã sửa** | CAP ≥ 302 dB/m, loại rượu có hại, viêm gan B/C, chưa kiểm định trên người Việt: có dưới kết quả và ở trang Giới thiệu |
| L7 Bấm lại mục Nghiên cứu | **Đã sửa nội dung** | Hiện Tổng quan; nhưng khi đó không mục nào được tô sáng (nhỏ) |
| L8 Biểu đồ baseline cộng dồn | **Đã sửa** | Cột đặt cạnh nhau, trục 0–0,8 (`anh/07`) |
| L9 Không báo điền thiếu | **Đã sửa** | "Đã điền x/19 số đo", "Đang thiếu x/19", cảnh báo mạnh khi thiếu cả BMI, eo, mông |
| L10 Lỗi hiện mã NHANES | **Đã sửa** | "Tuổi…, Giới tính…, Chủng tộc / dân tộc…"; dấu * đúng 3 trường; nhóm có lỗi tự mở |
| L11 G3/G4 bắt buộc | **Đã sửa** | Có "Không rõ" → bộ điền thiếu học từ TRAIN; 1.004/1.004 VAL qua |
| L12 Phụ thuộc thư mục tests | **Đã sửa** | 12 ca nền chuyển sang `artifacts/`, trùng byte bản cũ; xóa `tests/` giải thích vẫn chạy |
| L13 Thiếu tài nguyên làm sập | **Đã sửa** | 6/6 ca; `showErrorDetails = "none"` |
| L14 `thresholds.json` bị ghi đè | **Đã sửa** | Chỉ còn Fusion (b), giá trị không đổi. Trường `created_at` vẫn ghi 08/10 của bản bị ghi đè dù tệp được sửa ngày 03/11 |
| L15 Hiệu chuẩn | **Sửa một phần** | Số 1,40 và +0,27 khớp `KetQua_Tuan8/loi/hieu_chuan.csv` (1,3982; 0,2654); chưa nói cách đọc độ dốc > 1 |
| L16 Nhãn dương/âm tính | **Đã sửa** | "Trên/Dưới ngưỡng nguy cơ nghiên cứu"; PPV 58,17%, NPV 89,01% khớp ma trận nhầm lẫn đã lưu (TP 203, FP 146, TN 583, FN 72). Còn sót tiêu đề "Dương tính / âm tính…" ở trang Giải thích |
| L17 Chủng tộc | **Đã sửa** | Ghi chú nằm trong phần trợ giúp của ô (chỉ hiện khi rê chuột vào dấu ?) |
| L18 Thiếu hình | **Sửa phần lớn** | Có kiến trúc, SHAP nhóm, beeswarm, waterfall TP/FN, ablation TEST, VAL–TEST. Hình hiệu chuẩn và ma trận nhầm lẫn được thêm vào gói nhưng không hiển thị |
| L19 Không có test giao diện | **Sửa một phần** | Có test AppTest nhưng 2/3 hỏng (N2) |
| L20 Phiên bản Streamlit | **Đã sửa** | Ghim `streamlit==1.66.1`; không còn `use_container_width`; nút điều hướng trên điện thoại thấp hơn |

Lỗi nhỏ của v2 đã sửa: câu chỉ dẫn sai tên mục, số dòng CSV khi có dòng trống, tệp xuất có ngưỡng và tên mô hình, vạch ngưỡng trên thanh xác suất, ghi nguồn của kết quả xem từ CSV, nút Deploy. Còn nguyên: dấu thập phân lẫn lộn, tên cột thô ở bảng CV tuần 6 và bảng nhóm tuần 7, cách tính `diet_recall_missing` (không ảnh hưởng xác suất).

---

## 4. Lỗi mới hoặc còn lại

### Phải sửa trước khi đưa lên GitHub hoặc ghi nghiệm thu

**N1 — Clone bằng Git trên Windows làm web từ chối dự đoán.** Manifest nay băm thêm 3 JSON và 1 CSV, nhưng `.gitattributes` chỉ khóa `.joblib` và ảnh. Máy này, cũng như mặc định của Git for Windows, đặt `core.autocrlf = true`: khi clone, 4 tệp trên đổi xuống dòng LF thành CRLF, khác SHA-256, web báo "Không thể xác minh mô hình đã khóa" và dừng (`ket_qua/b4.txt`, mục f). Đây đúng loại lỗi đã gặp ở PR #1 ngày 16/10. Chạy từ zip thì không bị.

Cách sửa đã thử trên bản sao (clone xong 4 tệp trùng byte, ca A 59,49%; `ket_qua/b4b_thu_sua_gitattributes.txt`): thêm vào cuối `.gitattributes`

```
artifacts/*.json -text
artifacts/*.csv -text
```

Nếu repo đã lưu các tệp này theo thuộc tính cũ, sau khi sửa cần chạy `git add --renormalize .` rồi commit.

**N2 — 2/3 test AppTest đi kèm bị hỏng.** `tests/test_streamlit_apptest_smoke.py` gọi `at.button(label=...)`; AppTest không có tham số này nên báo `TypeError` trước khi chạm tới web (`ket_qua/c2_pytest_apptest_cua_web.txt`). Biên bản sửa ghi các test này "chưa chạy", còn `TEST_PLAN_15.md` lại hướng dẫn chạy chúng. Sửa: tìm nút theo nhãn, ví dụ `next(b for b in at.button if b.label == 'Thử ca A · trên ngưỡng')`. Script `ma_kiem/b5_apptest_luong_giao_dien.py` (40 bước, đều đạt) cho thấy bản thân web không lỗi và có thể dùng làm mẫu.

### Nên sửa

**N3 — Số đo thấp bất thường hoặc nhập theo inch vẫn cho kết quả.** Giới hạn kỹ thuật rộng hơn nhiều so với TRAIN ở đầu thấp: eo từ 30 cm (TRAIN 56,4), mông từ 30 cm (TRAIN 74), BMI từ 5 (TRAIN 14,9). Ca A nhập eo 44 (inch, tức 112 cm) cho 22,43%, dưới ngưỡng; eo 30 cho 22,29%; BMI 12 cho 33,60% (`ket_qua/b3.txt`, `b7.txt`). Web có cảnh báo "ngoài khoảng TRAIN", nhưng cảnh báo nằm dưới thẻ kết quả. Đề xuất: với BMI, eo, mông (nhóm G1 chiếm 64,5% trọng số) nằm ngoài khoảng TRAIN thì chặn hoặc bắt tích xác nhận, và đưa cảnh báo lên trên con số.

**N4 — Kiểm dấu hàng nghìn chỉ áp cho 4 xét nghiệm mỡ máu và đường huyết.** GGT `1,192` được hiểu là 1,192 U/L (ca A còn 45,66%); ALT `1.000` thành 1 (50,80%). Có cảnh báo ngoài khoảng TRAIN nhưng vẫn ra kết quả. Đề xuất áp quy tắc này cho mọi ô số có thể vượt 999.

### Nhỏ

- Trang Nghiên cứu: bấm lại mục đang chọn thì nội dung đúng nhưng không mục nào sáng (cả 4 nút `aria-checked=false`).
- Xem một dòng CSV sẽ thay kết quả nhập tay vì web chỉ có một ô "kết quả gần nhất"; tab nhập tay khi đó không hiện gì.
- Bảng xem trước CSV có dòng lỗi trộn số và chữ, Streamlit ghi traceback Arrow ra terminal mỗi lần chạy lại (người dùng không thấy).
- Tài liệu lệch: `resource/research/SOURCES.md` vẫn ghi TEST "không được đưa vào ứng dụng"; `danh_gia_gop_val_test.csv` chỉ được nêu tên; `bon_goc_nhin_nhom.csv` và 10 hình (trong đó có 2 hình mới thêm: hiệu chuẩn, ma trận nhầm lẫn) không được dùng.
- Câu chữ: tiêu đề "Dương tính / âm tính…" ở trang Giải thích; thông báo "vượt phạm vi" dùng cả cho giá trị quá thấp; chú thích "Đã điền 15/19 số đo…" kèm câu "Không dùng ngưỡng này như ngưỡng y khoa" không liên quan; dấu thập phân vẫn lẫn `59.49%` và `33,16%`; bảng VAL–TEST bỏ số 0 cuối (0,645; 0,691).
- 191/1.004 người VAL (19%) sẽ thấy câu "độ tin cậy… chưa được kiểm chứng", kể cả khi chỉ thiếu 1/19 số đo. Có thể chia mức cảnh báo.
- Điện thoại 375 px: không tràn ngang; nút dự đoán ở khoảng 2.850 px tính từ đầu trang.
- README dùng `.venv\Scripts\activate`, lệnh này có thể bị ExecutionPolicy của PowerShell chặn; gọi thẳng `.venv\Scripts\python.exe` an toàn hơn.

---

## 5. Những phần tốt, nên giữ

- Chuỗi suy luận không đổi so với v2 (`src/inference.py`, 5 `.joblib`, `weights.json`); phần kiểm nhập mới không làm lệch xác suất của người nào trong VAL.
- Giới hạn kỹ thuật không chặn người nào trong 4.680 TRAIN; khoảng cảnh báo TRAIN trùng đúng min–max thực tế.
- 7777 và 9999 phút ngồi được coi là thiếu, đúng quy tắc nghiên cứu; số 0 dạng SAS được chuẩn hóa.
- Thông báo lỗi tiếng Việt, không lộ đường dẫn máy; trang không sập khi thiếu tài nguyên.
- Phần TEST chỉ đọc bảng đã lưu, không nạp dữ liệu TEST; mọi số kiểm được đều khớp tệp nguồn.

---

## 6. Thứ tự đề xuất

Tạo bản mới, không ghi đè V3, không đổi mô hình, trọng số, ngưỡng.

1. N1: thêm 2 dòng vào `.gitattributes`; thử clone thật trên Windows.
2. N2: sửa test AppTest; chạy với `RUN_APPTEST=1`.
3. N3, N4 nếu nhóm đồng ý siết kiểm nhập.
4. Sửa tài liệu và câu chữ ở mục "Nhỏ".
5. Chạy lại: bộ test, AppTest, 1.004 VAL, ca A/B/C (59,49% / 2,32% / 31,14%); sau đó nghiệm thu 15 luồng có ảnh chụp và cập nhật `TEST_PLAN_15.md`.
