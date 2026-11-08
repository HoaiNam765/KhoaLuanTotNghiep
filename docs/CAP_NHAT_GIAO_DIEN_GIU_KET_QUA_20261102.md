# NAFLD Insight — chỉnh bố cục và giữ kết quả trong phiên (02/11/2026)

## Chức năng thay đổi

- **Trang Giới thiệu:** hai phần giới thiệu và “Công cụ minh bạch” được căn thẳng hàng trên màn hình lớn; thống kê, ba bước và bốn nhóm sử dụng các thẻ có chiều cao đồng đều. Trên màn hình hẹp, chiều cao thẻ tự thay đổi để không cắt chữ.
- **Trang Dự đoán:** hỗ trợ 2 nút riêng `Xóa kết quả` (giữ nguyên 26 ô nhập) và `Nhập ca mới` (xóa dữ liệu trong 26 ô nhập và kết quả). Hai nút cũng xuất hiện ngay dưới kết quả để không cần cuộn lên.
- **Giữ dữ liệu qua điều hướng:** dữ liệu 26 ô nhập được đồng bộ vào khóa `draft_inputs` độc lập với widget. Do đó khi sang Giải thích / Nghiên cứu rồi quay về Dự đoán, các ô vẫn giữ giá trị trong **cùng phiên Streamlit**.
- **Giữ kết quả:** `last_prediction`, `last_case`, `last_source`, `last_time` và `local_explanation` có thể được xem lại ở trang Giải thích. Khi thay đổi form mà chưa dự đoán lại, trang Dự đoán thông báo rõ kết quả cũ không áp dụng cho dữ liệu vừa chỉnh.
- **CSV:** tệp tải lên và các kết quả dự đoán giữ lại trong phiên khi chuyển trang. `Bỏ tệp CSV` xóa bản CSV đã lưu trong phiên và bảng dự đoán của tệp đó.

## Lưu ý bảo mật và phương pháp

Không lưu hồ sơ hoặc tệp CSV vào cơ sở dữ liệu/ổ đĩa, và không bổ sung dữ liệu nhập vào TRAIN, OOF, VAL hay bảng thống kê nghiên cứu. Đây là **lưu trong session**, không phải lưu tài khoản hay lưu vĩnh viễn; đóng phiên, làm mới toàn bộ phiên hoặc restart Streamlit có thể xóa dữ liệu. Tránh nhập thông tin định danh của người bệnh thật vào bản demo. `Xóa kết quả` không huấn luyện lại hoặc tác động đến model.

Giữ nguyên Fusion (b) seed 42, các trọng số, ngưỡng F1 OOF, dữ liệu nguồn nghiên cứu và chức năng giải thích SHAP đã có.

## Kiểm thử

Chạy từ thư mục `KhoanLuanTotNghiep`:

```cmd
python -m pytest -q tests
python -m streamlit run app\app.py
```

Các kiểm thử Python xác nhận bộ trạng thái bền qua việc xóa widget, nút đặt lại và việc thay CSV; vẫn cần kiểm thử trực tiếp trên trình duyệt (Windows và mobile) để nghiệm thu đầy đủ hành vi và responsive.
