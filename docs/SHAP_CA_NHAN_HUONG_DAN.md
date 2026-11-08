# Giải thích cục bộ cho một ca nhập — NAFLD Insight

## Phạm vi và tính trung thực khoa học

- **SHAP toàn cục từ VAL Tuần 9** giữ nguyên các hình và bảng gốc tại `resource/`. Không tạo mới hoặc thay thế bộ kết quả nghiên cứu đã khóa.
- **Giải thích cho ca nhập** là **xấp xỉ Shapley bằng hoán vị** (Monte Carlo permutation) trong không gian **xác suất dự đoán** của Fusion (b), dựa trên **12 trường hợp VAL cố định** trong `tests/fixture_val_raw12.csv`. Không gọi đây là kết quả SHAP chính thức của Tuần 9, cũng không gọi là TreeSHAP.
- Gom 43 đặc trưng thành 26 biến gốc, bao gồm mã one-hot và cờ thiếu dữ liệu; thay từng nhóm biến gốc theo thứ tự hoán vị trong các tổ hợp lai với dữ liệu nền. Sử dụng 24 hoán vị (12 cặp thuận-nghịch) và seed42 để kết quả lặp lại được.
- Giá trị được biểu diễn bằng **điểm phần trăm xác suất** (probability points): `p_ca = p_nen + tổng(đóng góp của 26 biến)`; kiểm tra sai lệch <= 1e-9. Đây là phép phân rã toán học của dự đoán trên tập nền đã chọn, không phản ánh quan hệ nhân quả. Bộ nền nhỏ có thể làm các đóng góp không ổn định.
- Không dùng TRAIN hoặc TEST trong quá trình tính giải thích trên ứng dụng. Không thay đổi các tệp `artifacts/*.joblib`, trọng số nhóm, ngưỡng, mô hình đã huấn luyện hoặc logic `src/inference.py`.

## Sử dụng

1. Chạy `python -m streamlit run app/app.py`; trên trang **Dự đoán nguy cơ**, nhập một ca, chọn chế độ ngưỡng và bấm **Phân tích nguy cơ**.
2. Mở mục **Giải thích các yếu tố cho lần nhập này (Shapley xấp xỉ)** ở ngay dưới kết quả, rồi bấm **Tính giải thích cho ca này**. Hoặc chuyển sang **Giải thích SHAP** → **Theo ca nhập · Shapley xấp xỉ**.
3. Xem xác suất nền, xác suất ca nhập, biểu đồ thay đổi xác suất top 12, bảng đóng góp G1–G4 và bảng chi tiết 26 biến.
4. Khi thay đổi dữ liệu và dự đoán lại, giải thích trước đó bị xóa để tránh nhầm ca. Thay đổi ngưỡng phân loại không thay đổi giá trị xác suất hoặc các đóng góp khi cùng bộ dữ liệu.

## Kiểm thử

`python -m pytest -q tests`

Kiểm thử tự động kiểm tra phép ánh xạ 26→43 không trùng cột; đẳng thức cộng tính; tính ổn định theo seed; xác suất chính thức giữ nguyên; sai schema bị từ chối. 15 luồng UI vẫn cần nghiệm thu bằng thao tác thật, đặc biệt T14 hiển thị ba biểu đồ SHAP toàn cục cũ và tab giải thích ca vừa nhập mới.

## Giới hạn y khoa

Mô hình nghiên cứu dự đoán nhãn NAFLD trên quần thể khảo sát đã chọn, không chứng minh người nhập mắc hay không mắc NAFLD; không phân biệt NAFLD với bệnh gan do rượu. Không dùng đầu ra để tự quyết định điều trị.
