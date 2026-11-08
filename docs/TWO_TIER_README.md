> **LƯU Ý 03/11/2026:** Tài liệu lưu trữ của giao diện trước. Xem `README.md` và `docs/FIX_V2_20261103.md` cho bản hiện hành.

# NAFLD Insight — Giao diện hai tầng (25/10/2026)

## Mục đích

Hỗ trợ hai nhóm đối tượng sử dụng cùng mô hình Fusion (b) đã khóa. Giao diện **Dành cho người dùng** ưu tiên sự dễ hiểu khi nhập dữ liệu và giải thích kết quả. Giao diện **Dành cho nhà nghiên cứu** công bố minh chứng đã lưu, không chạy lại huấn luyện.

## Cách mở

```bash
python -m pip install -r requirements.txt
python -m pytest -q tests
python -m streamlit run app/app.py
```

Trong sidebar chọn **Không gian làm việc**:

- **Dành cho người dùng**: Tổng quan → Dự đoán nguy cơ → Giải thích SHAP → Về mô hình.
- **Dành cho nhà nghiên cứu**: Tổng quan nghiên cứu → So sánh mô hình → Đóng góp & SHAP → Nguồn dữ liệu & kiểm định.

Truy cập theo địa chỉ Streamlit hiển thị (mặc định `http://localhost:8501`). Không yêu cầu đường dẫn ổ đĩa cố định.

## Nguồn của tầng nhà nghiên cứu

| Trang / tab | Nguồn thực tế | Phạm vi |
|---|---|---|
| Baseline | Tuần 5 `chi_so_baseline.csv` | VAL (lọc theo `tap == val`) |
| Kiểm định chéo | Tuần 6 `cv_screen.csv` | TRAIN, Stratified 5-fold CV |
| Trước / sau tinh chỉnh | Tuần 6 `so_sanh_truoc_sau_tinh_chinh.csv` | TRAIN CV |
| Fusion, Stacking | Tuần 7 `bang_so_sanh_val.csv` | VAL, 5 seed |
| AUPRC OOF | Tuần 7 `auprc_tren_oof.csv` | OOF trên TRAIN |
| G1–G4 độc lập | Tuần 7 `bang_nhom_don_le.csv` | VAL |
| Ablation Fusion (b) | Tuần 8 `tong_hop_fusion_b_ablation.csv` | VAL (trọng số được tối ưu lại khi bỏ nhóm) |
| SHAP toàn cục | Tuần 9 `final_shap_tuan9.csv` | VAL |

Chi tiết đường dẫn và cách đối chiếu: [`resource/research/SOURCES.md`](../resource/research/SOURCES.md).

## Nguyên tắc diễn giải

- AUPRC, AUROC độc lập với ngưỡng; Accuracy/Precision/Recall/F1 phụ thuộc ngưỡng. Không so trực tiếp kết quả OOF và VAL như thể cùng một phép thử.
- SHAP toàn cục từ VAL tuần 9 khác phương pháp Shapley hoán vị xấp xỉ của một ca nhập. Không diễn giải SHAP như bằng chứng nhân quả.
- G3 và G4 có trọng số tối ưu gần 0 trong Fusion (b) seed 42. Không kết luận bệnh nền hoặc lối sống không có liên quan sinh học.
- Phân loại vượt hoặc dưới ngưỡng không đồng nghĩa với chẩn đoán mắc hay không mắc NAFLD. Hệ thống không phân biệt gan nhiễm mỡ do rượu hoặc các căn nguyên khác.

## Những gì đã kiểm thử và chưa kiểm thử

- `pytest` kiểm tra tính toàn vẹn và hồi quy của mô hình đã khóa, phép cộng đóng góp Shapley, các nguồn CSV trong tầng nghiên cứu. Bản thay đổi này thêm bốn unit test nguồn minh chứng.
- **Chưa** xác nhận nghiệm thu 15/15 luồng qua trình duyệt và chạy offline trên máy độc lập. Phải thực hiện kịch bản tuần 11 với ảnh minh chứng và báo cáo trước khi công bố PASS UI.

## Tích hợp GitHub

Khuyến nghị mở branch riêng `feature/two-tier-medical-research-ui` trước khi commit, để có thể review lại diff với phiên bản hiện tại. Không ghi đè hoặc thay đổi `artifacts/`, `src/inference.py` và tập TEST.
