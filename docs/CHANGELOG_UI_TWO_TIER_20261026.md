# Cập nhật UI hai tầng — 26/10/2026

## Sửa giao diện nhập liệu

- Chuyển toàn bộ danh mục lâm sàng và chế độ ngưỡng từ `st.selectbox` (có ô tìm kiếm nội bộ, caret và nút xóa) sang `st.radio` dạng lựa chọn tường minh. Không thể gõ mã danh mục ngoài danh sách; các danh mục lâm sàng không có lựa chọn mặc định.
- Tuổi (`RIDAGEYR`) và thời gian ngồi (`PAD680`) dùng `int`, `step=1`, `format="%d"`; tuổi bắt buộc 18–80. Các số đo khác dùng `format="%g"` để không hiển thị số 0 vô nghĩa ở phần thập phân (ví dụ 35 thay vì 35,00; 35,5 khi có số lẻ). Số đo vẫn là số thực trong pipeline gốc. Không thay đổi giá trị đầu vào khi dự đoán.
- Trang người dùng có biểu đồ bốn mô hình baseline và nút mở trực tiếp tầng nghiên cứu. Tầng nghiên cứu tiếp tục có bốn tab: baseline VAL tuần 5, CV tuần 6, so sánh Fusion/Stacking VAL tuần 7, OOF tuần 7.

## Giới hạn và bảo đảm nghiên cứu

- Biểu đồ mới lấy đúng bốn hàng VAL từ `resource/research/baseline_val_week5.csv`, không gộp TRAIN với VAL, không tạo chỉ số mới.
- Không chạy lại baseline theo ca nhập. Để hiển thị xác suất baseline theo từng ca cần thêm model/pipeline baseline đã đóng băng và các kiểm thử đối chiếu VAL trước khi tích hợp.
- `artifacts/*.joblib`, `artifacts/weights.json`, `artifacts/thresholds.json`, `artifacts/groups.json`, `artifacts/manifest.json`, `src/inference.py` và `src/local_explain.py` được giữ nguyên.
- Bắt buộc kiểm tra trên máy chạy Streamlit: hành vi radio/range ở form, 15/15 luồng, chạy offline và thời gian dưới 5 giây. Unit test không thay thế kiểm thử trình duyệt.

## Lệnh chạy (tại thư mục gốc repository)

```cmd
python -m pip install -r requirements.txt
python -m pytest -q tests
python -m streamlit run app/app.py
```

## Tệp đã sửa

- `app/app.py`
- `src/ui_specs.py` (mới)
- `src/research_evidence.py`
- `tests/test_ui_and_comparison.py` (mới)
- `docs/CHANGELOG_UI_TWO_TIER_20261026.md` (mới)
