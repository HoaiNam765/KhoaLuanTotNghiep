# NAFLD Insight — Giao diện hai tầng dễ sử dụng (01/11/2026)

## 1. Thay đổi chính

- Giao diện sáng, trung tính, ít hiệu ứng: xanh rêu `#176A72`, nền ngà `#F7F8F6`, chữ xanh than `#1B3137`, viền nhẹ và màu nâu đất dành cho biểu đồ giảm xác suất. Tách nội dung thành **Giới thiệu · Dự đoán · Giải thích · Nghiên cứu**, không dùng ảnh nền hoặc icon emoji trang trí.
- **Chỉ một nút “Xem kết quả dự đoán”**. Người dùng không cần chọn ba ngưỡng. Mặc định luôn dùng **F1 OOF, 0,3315983622** từ `artifacts/thresholds.json`, không thêm/chỉnh sửa ngưỡng. Trang nghiên cứu vẫn công bố cả ba mốc, cùng giải thích cách chọn.
- Kết quả hiển thị **Dự đoán dương tính/âm tính theo mô hình**, xác suất và lời giải nghĩa; không đưa ra chẩn đoán bệnh. Tín hiệu bốn nhóm, Shapley cục bộ được đặt trong khu vực giải thích tùy chọn.
- Form nhập 26 biến được nhóm thành bốn phần có thể mở rộng. Số thập phân cho phép dấu chấm hoặc phẩy, số chưa có có thể để trống; tuổi 18–80 và bảy danh mục là bắt buộc. Không dùng giá trị mặc định giả như “18,00”.
- Nút nạp **hai ca giả lập A/B** dùng cho demo, không phải dữ liệu bệnh nhân. Đã đối chiếu xác suất với mô hình bất biến.
- **CSV**: tải mẫu 26 cột mã NHANES, nhập tối đa 100 dòng / lần (1 MB), CSV UTF-8 phân cách `,` hoặc `;`; danh mục chấp nhận mã số hợp lệ hoặc nhãn tiếng Việt theo mẫu; số có dấu phẩy thập phân trong CSV phân cách `;`; xem trước, báo lỗi theo dòng, chỉ dự đoán dòng hợp lệ, tải bảng kết quả rút gọn. Không đưa dữ liệu CSV lên bảng nghiên cứu hoặc ghi xuống ổ đĩa.
- **Tầng nghiên cứu** được tổ chức lại thành tổng quan, so sánh, đóng góp và nguồn/kiểm định; hiển thị chỉ số gốc trên TRAIN-CV, OOF và VAL, không trộn các miền đánh giá.

## 2. Cách chạy

Mở terminal tại thư mục chứa `requirements.txt`:

```bash
python -m pip install -r requirements.txt
python -m pytest -q tests
python -m streamlit run app/app.py
```

Vào `http://localhost:8501`.

**Tương thích:** bộ `.joblib` lưu bằng scikit-learn **1.9.0**, nên phải dùng đúng `requirements.txt`, không tùy tiện nạp bằng các phiên bản khác. Để chuyển máy, giải nén nguyên thư mục và cài môi trường tương thích.

## 3. Ví dụ nhập CSV

1. Chọn **Dự đoán → Nhập từ tệp CSV**.
2. Chọn **Tải CSV mẫu** (có 2 ca giả lập) và mở bằng Excel.
3. Giữ nguyên tên 26 cột mã NHANES, mỗi dòng một trường hợp.
4. Những phép đo số không có dữ liệu: để ô rỗng, **không nhập số 0**. Các cột danh mục bắt buộc phải có mã hợp lệ.
5. Lưu dưới dạng **CSV UTF-8**, tải lên, kiểm tra lỗi và nhấn **Dự đoán những dòng hợp lệ**.
6. Xuất CSV kết quả hoặc chọn một dòng để xem tín hiệu và giải thích cục bộ. Tệp xuất **không chứa lại thông tin đầu vào**.

Cột CSV chính xác gồm: `RIDAGEYR,BMXBMI,BMXWAIST,BMXHIP,BPXOSY1,BPXODI1,LBXSASSI,LBXSATSI,LBXSGTSI,LBXSTR,LBDHDD,LBXTC,LBXSGL,LBXGH,PAD680,DR1TKCAL,DR1TSUGR,DR1TSFAT,DR1TFIBE,RIAGENDR,RIDRETH3,BPQ020,BPQ080,GLYCEMIC_HX,PAQ650,SMOKE_STATUS`.

Nhập dữ liệu nhạy cảm chỉ khi có sự đồng ý của người cung cấp. Dữ liệu có thể nằm tạm trong **bộ nhớ phiên Streamlit trên máy chủ** tới khi phiên kết thúc; bản demo **không lưu lâu dài** hoặc đồng bộ vào kho nghiên cứu. Không nên triển khai công khai để xử lý bệnh án thật khi chưa có giải pháp bảo mật/pháp lý đầy đủ.

## 4. Bất biến khoa học

- Giữ nguyên toàn bộ `.joblib`, `manifest.json`, `groups.json`, `weights.json`, `thresholds.json`, `src/inference.py` và `src/local_explain.py`.
- Không đọc tập TEST, không huấn luyện lại, không thay đổi 26→43 đặc trưng.
- Nguồn chỉ số bảng nghiên cứu: `resource/research/` và SHAP tuần 9 trong `resource/final_shap_tuan9.csv`.
- Không hiểu xác suất mô hình là nguy cơ thực tế đã hiệu chuẩn; không chẩn đoán NAFLD hay phân biệt căn nguyên gan nhiễm mỡ.

## 5. Kiểm thử

- `pytest` xác minh bất biến suy luận, hồi quy hai ca A/B, parsing CSV, lỗi hàng, cột, định dạng, số nguyên, missing ≠ 0, không đưa input thô vào tệp xuất.
- Chưa thực hiện nghiệm thu tương tác Streamlit trên trình duyệt tại môi trường tạo bản này vì môi trường không cài `streamlit` và không thể tải thêm gói từ internet. Cần kiểm tra thủ công responsive, 15 luồng UI, máy khác và thời gian suy luận trước khi nghiệm thu khóa luận.
