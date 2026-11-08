# NAFLD Insight V3 — Bản cập nhật theo đánh giá ngày 07/11/2026

Ứng dụng Streamlit minh họa **Fusion (b), seed 42** từ 26 biến lâm sàng NHANES. Không chẩn đoán hay điều trị. Không huấn luyện lại model, không thay trọng số hoặc ngưỡng F1 OOF đã khóa. Các kết quả TEST chỉ là **bảng và hình tổng hợp có sẵn**, tuyệt đối không dự đoán lại từ TEST trong website.

## Cài đặt và chạy (Python 3.13)

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pytest -q tests
.\.venv\Scripts\python.exe -m streamlit run app/app.py
```

Không cần kích hoạt môi trường ảo; gọi trực tiếp Python trong `.venv` giúp tránh lỗi ExecutionPolicy của PowerShell. Để chạy riêng các bài AppTest (cần cài đúng Streamlit trong `requirements.txt`):

```powershell
$env:RUN_APPTEST='1'
.\.venv\Scripts\python.exe -m pytest -q tests/test_streamlit_apptest_smoke.py
Remove-Item Env:RUN_APPTEST
```

Truy cập http://localhost:8501 . Khi chạy AppTest, chỉ bật `RUN_APPTEST=1` cho lệnh kiểm thử giao diện rồi xóa biến môi trường sau khi chạy. Không chạy `docs/tham_khao_app_tuan11/nafld_du_doan.py`.

## Giao diện hiện tại

- **Giới thiệu**: phạm vi CAP >= 302 dB/m, nguồn dữ liệu và giới hạn lâm sàng.
- **Dự đoán**: nhập tay hoặc CSV tối đa 100 dòng; có 3 trường bắt buộc (tuổi/giới tính/nhóm dân tộc NHANES), các danh mục bệnh nền/lối sống có thể chọn “Không rõ”. Số đo thiếu để trống (không gõ 0). Dấu phẩy hoặc chấm là dấu thập phân, không dùng dấu ngăn cách hàng nghìn; chuỗi số mơ hồ dạng `1,200`/`1.200` ở các trường có thể vượt 999 sẽ bị yêu cầu nhập lại. BMI/vòng eo/vòng mông ngoài khoảng quan sát TRAIN cần xác nhận trước khi dự đoán.
- **Kết quả**: nhãn trên/dưới ngưỡng F1 OOF 33,16%; cảnh báo đơn vị, phạm vi TRAIN và số đo thiếu được hiển thị trước xác suất; giải thích Shapley xấp xỉ từ 12 mẫu VAL lưu trong `artifacts/`.
- **Nghiên cứu**: kết quả TRAIN CV, OOF, VAL, TEST (chỉ bảng tổng hợp đã lưu), kiến trúc Fusion, ablation, SHAP.
- Hình logo/cover/research cố định tại `app/assets/`; không có nút tải ảnh giao diện.

## Bảo vệ nghiên cứu

`artifacts/manifest.json` chứa SHA256 cho 5 joblib, 3 JSON cấu hình và 12 mẫu VAL tham chiếu. Những tệp này bị thay đổi phải cập nhật đúng nguồn có thẩm quyền; **không chỉnh thủ công trọng số/ngưỡng rồi tạo lại manifest**. Dữ liệu form/CSV không lưu xuống ổ đĩa hoặc thêm vào tập nghiên cứu. Khả năng tổng quát sang người Việt Nam chưa được xác thực.

`artifacts/thresholds.json` chỉ chứa các ngưỡng Fusion (b), các ngưỡng nghiên cứu khác đã bị loại khỏi gói vì bị ghi sai ở bản web cũ; giá trị Fusion (b) seed 42–46 giữ nguyên. Những cảnh báo biên hợp lý trong giao diện là bảo vệ nhập liệu, không phải giới hạn/khuyến cáo lâm sàng.

## Kiểm thử và tài liệu

- `docs/FIX_V2_20261103.md` — biên bản sửa V2 ban đầu.
- `docs/FIX_V3_20261107.md` — các điều chỉnh và kết quả kiểm tra theo đánh giá V3 ngày 07/11/2026.
- `docs/07_DANH_GIA_WEB_V3.md` — báo cáo đánh giá gốc.
- `tests/TEST_PLAN_15.md` — danh sách nghiệm thu UI cập nhật.
- `resource/research/` — kết quả đã lưu và mô tả nguồn, trong đó có bảng tổng hợp TEST từ tuần 9.

**Kết quả TEST không chứng minh Fusion (b) tốt hơn LightGBM gộp:** trung bình 5 seed, AUPRC TEST lần lượt 0,6881 và 0,6910. Fusion (b) vẫn là mô hình minh họa chính vì cấu trúc dễ diễn giải theo nhóm.
