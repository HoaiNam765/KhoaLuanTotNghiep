# Kế hoạch nghiệm thu NAFLD Insight V3 (07/11/2026)

Trạng thái: **CHƯA ĐÁNH DẤU PASS UI** trên trình duyệt Windows. Bảng này là test plan, không phải kết quả thực hiện. Mục tiêu 15 luồng chính + bổ sung các lỗi mới từ 06_DANH_GIA_WEB_V2.md. KHÔNG lấy dữ liệu TEST để chạy lại, chỉ dùng bảng số liệu TEST đã lưu.

| ID | Luồng | Tiêu chí PASS |
|---|---|---|
| T01 | Giới thiệu và kiến trúc | Header, ảnh cover/branding, 4 nhóm và giới hạn CAP rõ; hình kiến trúc xem được tại Nghiên cứu → Đóng góp & SHAP |
| T02 | Form 26 biến | Đúng 8/8/3/7 biến G1/G2/G3/G4; đánh dấu bắt buộc chỉ tuổi, giới tính và chủng tộc/dân tộc |
| T03 | Ca A và B | Thử ca A ≈ 59,49%, B ≈ 2,32%; không có sai lệch xác suất sau chỉnh UI |
| T04 | Thiếu huyết áp | Tham số fit trên TRAIN, cờ `BPXOSY1_was_missing` đúng; kết quả có ghi cảnh báo thiếu |
| T05 | Thiếu khẩu phần | Cờ `diet_recall_missing` đúng; hiển thị cảnh báo số phép đo còn thiếu |
| T06 | Biên nhập tay | Tuổi 17/81, BMI 0/345, vòng eo 1,12/11200, HA 80/140, HbA1c 61, ngồi 2000: CHẶN, báo tiếng Việt; 7777/9999 của phút ngồi → thiếu. BMI/eo/mông ngoài khoảng TRAIN nhưng trong hard limit phải yêu cầu xác nhận trước khi dự đoán. |
| T07 | Nhập dấu thập phân | 34,5 và 34.5 đều như nhau; chuỗi có dạng phân nhóm hàng nghìn như `1,200` hoặc `1.200` ở mọi trường số có giới hạn trên >999 phải yêu cầu nhập lại rõ ràng. |
| T08 | Mã danh mục | Giới tính 1/2 khớp; 5 danh mục G3/G4 có “Không rõ” và backend nhận None; mã lạ vẫn chặn |
| T09 | Khớp mô hình | Đúng 26 biến → 43 cột cùng thứ tự, không retrain, trọng số và ngưỡng seed 42 giữ nguyên |
| T10 | VAL regression | Dùng dữ liệu VAL nghiên cứu khi có sẵn, so xác suất với bản gốc; các ca hợp lệ giữ chênh ≤ 1e-10, ghi rõ trường hợp bị UI chặn/cảnh báo |
| T11 | F1 OOF mặc định | Ca A theo ngưỡng 33,16%, có vạch ngưỡng trên thanh; không có bộ chọn ngưỡng cho người dùng |
| T12 | Nghiên cứu: ngưỡng và TEST | 3 mốc nghiên cứu đúng JSON; bảng VAL–TEST đã lưu được gắn nguồn; Fusion (b) 0,6881 và LightGBM 0,6910 trên TEST, không tuyên bố thắng |
| T13 | CSV nhiều dòng → xem chi tiết | Tải mẫu, nhập CSV, kiểm lỗi, dự đoán, bấm “Hiển thị giải thích cho dòng này” khi ca nhập tay vẫn còn hiệu lực: không lỗi DuplicateElementKey; xuất đủ ngưỡng, version |
| T14 | SHAP | Biểu đồ tuần 9 đúng (global VAL), Shapley theo ca khác global; hiển thị hình SHAP nhóm, beeswarm và ví dụ; không nhận là quan hệ nhân quả |
| T15 | Nghiệm thu máy khác và responsive | Chạy từ thư mục mới (không dùng tests/ cho runtime), không lộ traceback/đường dẫn trên web; mobile 375 px không tràn, nút và ảnh đúng; benchmark môi trường triển khai riêng |

## Ca kiểm bổ sung quan trọng

- **B01:** Trên trang Nghiên cứu bấm lại mục đang chọn; không chuyển nhầm đến Nguồn & kiểm định.
- **B02:** Biểu đồ baseline AUROC/AUPRC không cộng dồn.
- **B03:** Đổi tệp JSON `weights.json` hoặc `thresholds.json` trên một **bản sao độc lập** → báo không thể xác minh mô hình. Tuyệt đối không thử trên bản gốc đang chạy.
- **B04:** Xóa `tests/` trong bản sao, giải thích Shapley vẫn hoạt động.
- **B05:** Đổi tên một ảnh bằng chứng trong bản sao → cảnh báo thân thiện, không lộ đường dẫn hệ thống.
- **B06:** Nhập giá trị mmol/L ở xét nghiệm yêu cầu mg/dL → cảnh báo hiển thị trước con số dự đoán; người dùng phải tự xác minh đơn vị.
- **B09:** Nhập BMI/vòng eo/vòng mông ngoài khoảng quan sát TRAIN → hiển thị khoảng tham chiếu và yêu cầu xác nhận trước khi chạy dự đoán (cả form tay và CSV).
- **B10:** Nhập chuỗi số mơ hồ dạng `1,200`/`1.200` cho các trường có giới hạn trên >999 → hệ thống yêu cầu nhập lại, không tự diễn giải dấu phân cách.
- **B07:** Nhập thiếu 3 biến BMI/vòng eo/vòng mông → cảnh báo mạnh (không coi kết quả là bằng chứng y khoa).
- **B08:** Nhập họ tên? Không có trường thu thập tên; CSV xuất không chứa dữ liệu lâm sàng đầu vào.

## Chạy tự động

```powershell
python -m pytest -q tests
$env:RUN_APPTEST="1"
python -m pytest -q tests/test_streamlit_apptest_smoke.py
Remove-Item Env:RUN_APPTEST
python -m streamlit run app/app.py
```

AppTest không thay thế kiểm thử browser thực. Phải lưu screenshot cho 15 luồng trước khi báo cáo PASS.
