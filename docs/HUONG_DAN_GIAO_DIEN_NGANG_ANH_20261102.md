> **LƯU Ý 03/11/2026:** Nút tải ảnh giao diện đã bỏ. Bản hiện tại chỉ dùng ảnh cố định `app/assets/logo.png`, `cover.png`, `research.png`. Các đoạn dưới đây mô tả phiên bản lịch sử. Xem `README.md` và `docs/FIX_V2_20261103.md`.

# NAFLD Insight · Bản điều hướng ngang và hình ảnh (02/11/2026)

## Những gì đã sửa thực sự

1. **Bỏ menu điều hướng trong sidebar:** bốn mục `Giới thiệu`, `Dự đoán`, `Giải thích`, `Nghiên cứu` chuyển thành **bốn nút điều hướng ngang**, có icon Material, trạng thái đang chọn và nút hoạt động thật. Sidebar mặc định đóng và không còn là cách điều hướng chính.
2. **Header:** nhận diện NAFLD Insight, phụ đề rõ ràng và nút **Ảnh & nhận diện**.
3. **Ảnh:** ba bộ tải ảnh PNG/JPEG/WebP cho `Logo/icon`, `Ảnh giới thiệu`, `Ảnh nghiên cứu`. Ảnh tải lên được kiểm tra dung lượng, nội dung, kích thước, chuẩn hóa về PNG và hiển thị ngay trong phiên. Không chấp nhận SVG/HTML từ người dùng.
4. **Giới thiệu:** hero nền xanh rất nhạt, cột nội dung/ảnh; thống kê 26 biến, 4 nhóm; ba bước sử dụng; bốn thẻ giải thích nhóm. Không có câu mô tả thiết kế dạng placeholder từ bản demo trước.
5. **Dự đoán:** bố cục chính + cột hướng dẫn, giữ hai chế độ nhập trực tiếp/CSV, ví dụ A/B, một nút dự đoán và ngưỡng F1 OOF mặc định.
6. **Nghiên cứu:** phần tổng quan có timeline 5 giai đoạn, có thể hiển thị ảnh riêng; menu nghiên cứu theo lựa chọn ngang; các bảng CV, Fusion, ablation, SHAP giữ dữ liệu nghiên cứu đã khóa.
7. **Responsive:** giảm kích thước nút, khoảng cách và các khối trên màn hình nhỏ, không dùng hiệu ứng thừa.

## Hướng dẫn chạy

Trong thư mục `KhoanLuanTotNghiep`:

```cmd
.venv\Scripts\activate
python -m pytest -q tests
python -m streamlit run app\app.py
```

Sau khi cập nhật file, nhấn `Ctrl+C` rồi chạy lại nếu Streamlit chưa cập nhật thay đổi Python. Truy cập `http://localhost:8501` và nhấn `Ctrl+F5` nếu CSS trình duyệt còn cache.

## Cách dùng logo/ảnh

Mở website → **Ảnh & nhận diện** (góc trên phải) → chọn ảnh. Phần giao diện tương ứng sẽ tự thay đổi. Chọn **Bỏ ảnh vừa tải** để dùng lại ảnh mặc định.

- Logo sẽ hiển thị ở thanh đầu trang mọi màn hình.
- Ảnh giới thiệu hiển thị bên phải nội dung trang Giới thiệu.
- Ảnh nghiên cứu hiển thị trong Nghiên cứu → Tổng quan.
- Tệp chỉ ở phiên Streamlit; không lưu vào train, val, test, database hoặc hồ sơ y khoa.

**Muốn ảnh cố định cho mọi lần chạy:** đặt `logo.png`, `cover.png`, `research.png` vào thư mục `app/assets/` (chi tiết xem `app/assets/README.md`).

## Nghiệm thu giao diện nên thực hiện trên Windows

- [ ] Bốn nút menu hiển thị thành **một hàng** trên màn hình desktop; icon và mục đang chọn dễ nhận biết.
- [ ] Nhấn cả bốn nút điều hướng được đến đúng trang và nhấn lại không xóa dữ liệu nhập.
- [ ] Logo mới hiển thị ngay ở header, ảnh giới thiệu ở trang Giới thiệu, ảnh nghiên cứu ở trang Nghiên cứu.
- [ ] Ảnh lớn hơn 2 MB hoặc không đúng định dạng bị chặn, website không bị lỗi.
- [ ] Trên mobile không tràn ngang trang, các nút vẫn đủ lớn và dễ bấm.
- [ ] Nhập ca A khoảng 59,49%, ca B khoảng 2,32%; không thay đổi các mô hình, tiền xử lý hoặc ngưỡng.
- [ ] Nhập CSV mẫu, dự đoán cả hai dòng, tải kết quả; không có dữ liệu nhập bị chèn vào trang nghiên cứu.

## Kiểm thử và phạm vi

`pytest` bao phủ mã Python, upload ảnh và không thay đổi kết quả dự đoán đã khóa. **Không xem đây là bằng chứng nghiệm thu 15 luồng UI hoặc pixel-perfect trên trình duyệt.**
