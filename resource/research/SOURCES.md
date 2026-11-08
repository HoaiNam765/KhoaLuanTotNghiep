# Nguồn minh chứng của bảng điều khiển nghiên cứu

Các bảng và hình trong thư mục này là bản sao từ hồ sơ nghiên cứu đã cung cấp. Ứng dụng chỉ **đọc** các tệp; không huấn luyện lại mô hình và không tính lại kết quả TEST từ dữ liệu cá nhân.

| Tệp được đóng gói | Vị trí nguồn gốc | Miền đánh giá / trạng thái |
|---|---|---|
| `baseline_val_week5.csv` | `KetQua_Tuan5_v2/bang/chi_so_baseline.csv` | VAL (riêng baseline lọc từ bảng gốc) |
| `cv_week6.csv` | `KetQua_Tuan6/cv/cv_screen.csv` | CV / OOF |
| `tuning_week6.csv` | `KetQua_Tuan6/cv/so_sanh_truoc_sau_tinh_chinh.csv` | CV / OOF |
| `model_comparison_val_week7.csv` | `KetQua_Tuan7/so_sanh/bang_so_sanh_val.csv` | VAL (riêng baseline lọc từ bảng gốc) |
| `group_val_week7.csv` | `KetQua_Tuan7/bang_nhom_don_le.csv` | VAL (riêng baseline lọc từ bảng gốc) |
| `oof_week7.csv` | `KetQua_Tuan7/so_sanh/auprc_tren_oof.csv` | CV / OOF |
| `fusion_ablation_val_week8.csv` | `KetQua_Tuan8/fusion_ablation/tong_hop_fusion_b_ablation.csv` | VAL |
| `val_vs_test.csv` | `KetQua_Tuan9/bang/val_vs_test.csv` | Bảng tổng hợp VAL–TEST đã lưu; chỉ đọc |
| `danh_gia_gop_val_test.csv` | `KetQua_Tuan9/bang/danh_gia_gop_val_test.csv` | Bảng nguồn VAL–TEST; đóng gói để đối chiếu, hiện không được ứng dụng đọc trực tiếp |
| `bon_goc_nhin_nhom.csv` | `KetQua_Tuan9/bang/bon_goc_nhin_nhom.csv` | Phân tích nhóm đặc trưng; đóng gói tham khảo, hiện không được ứng dụng đọc trực tiếp |
| `final_shap_tuan9.csv` | `KetQua_Tuan9/bang/final_shap_tuan9.csv` | SHAP trên VAL |

## Hình minh chứng

- `hinh_ablation.png`: `KetQua_Tuan8/hinh/hinh_ablation.png`, được hiển thị trong phần nghiên cứu.
- `hinh_hieu_chuan.png`, `hinh_ma_tran_nham_lan_test.png`: `KetQua_Tuan8/hinh/`, được đóng gói nhưng hiện chưa hiển thị trong giao diện.
- `hinh_val_vs_test.png`, kiến trúc Fusion và các hình SHAP: `KetQua_Tuan9/hinh/`, các hình được sử dụng nằm trong phần nghiên cứu.

**Giới hạn:** Các bảng/hình TEST là số liệu tổng hợp có sẵn trong hồ sơ nghiên cứu. Website không nạp hồ sơ cá nhân thuộc TEST, không suy luận lại TEST và không dùng TEST để chọn tham số hoặc ngưỡng. Kết quả TEST được trình bày để minh bạch đối chiếu, không phải bằng chứng rằng Fusion (b) tốt hơn LightGBM gộp.
