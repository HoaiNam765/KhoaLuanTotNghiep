# Ảnh cố định cho NAFLD Insight

Ứng dụng đã **bỏ nút "Ảnh & nhận diện" và bộ tải ảnh giao diện**. Logo và hình minh họa chỉ được đọc từ thư mục `app/assets/` theo các đường dẫn gán cứng trong `app/app.py`:

```python
BRAND_IMAGE_PATHS = {
    'logo': BRAND_ASSETS / 'logo.png',
    'cover': BRAND_ASSETS / 'cover.png',
    'research': BRAND_ASSETS / 'research.png',
}
```

- `logo.png`: cạnh chữ **NAFLD Insight** trên mọi trang (khuyến nghị ảnh vuông, nền trong suốt).
- `cover.png`: cột hình bên phải trang **Giới thiệu** (khuyến nghị ảnh ngang).
- `research.png`: minh họa trong **Nghiên cứu → Tổng quan** (khuyến nghị ảnh ngang).

**Cách dùng:** chép ảnh PNG vào `app/assets/` rồi đặt đúng tên. Hoặc sửa tên tệp ở `BRAND_IMAGE_PATHS` trong `app/app.py`. Không có thao tác tải ảnh trên website. Khi thay ảnh, chạy lại Streamlit (Ctrl+C rồi khởi động lại); cần thì Ctrl+F5 trên trình duyệt.

Các ảnh không bắt buộc. Nếu thiếu `logo.png`, header dùng biểu tượng SVG có sẵn như trước. Nếu thiếu `cover.png` hoặc `research.png`, ứng dụng dùng nội dung dự phòng và giữ bố cục. Ảnh không hợp lệ hoặc quá lớn cũng sử dụng giao diện dự phòng. **Chỉ sử dụng tệp `.png` thực sự** (không đổi tên `.jpg` sang `.png`).

Chức năng **nhập CSV dữ liệu lâm sàng** tại trang Dự đoán không bị ảnh hưởng và vẫn hoạt động bình thường. Ảnh không tham gia pipeline ML, không thay đổi dữ liệu nghiên cứu.
