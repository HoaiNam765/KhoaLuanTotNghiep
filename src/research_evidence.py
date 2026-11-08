"""Read-only frozen research evidence (TRAIN CV, OOF, VAL, stored TEST summary).

Never loads raw TEST predictions, retrains, or revises model/weights/threshold.
"""
from pathlib import Path
import pandas as pd
from .inference import ROOT

EVIDENCE = ROOT / "resource" / "research"
FILES = {
    "baseline": "baseline_val_week5.csv",
    "cv": "cv_week6.csv",
    "tuning": "tuning_week6.csv",
    "comparison_val": "model_comparison_val_week7.csv",
    "group_val": "group_val_week7.csv",
    "oof": "oof_week7.csv",
    "ablation_val": "fusion_ablation_val_week8.csv",
    "shap_global": "../final_shap_tuan9.csv",
}
SOURCE_DESCRIPTIONS = {
    "baseline": "Tuần 5 · chi_so_baseline.csv · chỉ hiển thị hàng VAL",
    "cv": "Tuần 6 · cv_screen.csv · TRAIN 5-fold Stratified CV",
    "tuning": "Tuần 6 · so_sanh_truoc_sau_tinh_chinh.csv · TRAIN 5-fold CV",
    "comparison_val": "Tuần 7 · bang_so_sanh_val.csv · VAL, trung bình 5 seed",
    "group_val": "Tuần 7 · bang_nhom_don_le.csv · VAL, trung bình 5 seed",
    "oof": "Tuần 7 · auprc_tren_oof.csv · OOF trên TRAIN",
    "ablation_val": "Tuần 8 · tong_hop_fusion_b_ablation.csv · chỉ VAL; tái tối ưu trọng số khi bỏ nhóm",
    "shap_global": "Tuần 9 · final_shap_tuan9.csv · global SHAP trên VAL",
    "test_summary": "Tuần 9 · val_vs_test.csv · Bảng AUPRC VAL–TEST đã khóa, không dự đoán lại TEST",
}


def load_evidence(name):
    if name not in FILES:
        raise KeyError("Nguồn minh chứng chưa đăng ký")
    path = (EVIDENCE / FILES[name]).resolve()
    if not path.is_relative_to((ROOT / "resource").resolve()):
        raise RuntimeError("Nguồn nằm ngoài thư mục resource")
    if not path.is_file():
        raise FileNotFoundError(f"Thiếu nguồn minh chứng: {path.name}")
    df = pd.read_csv(path, encoding="utf-8-sig")
    if df.empty:
        raise ValueError(f"Tệp {path.name} không có dữ liệu")
    # Original eight tables remain VAL/OOF/CV only; TEST summary uses a separate read-only loader.
    if name == "baseline":
        df = df.loc[df["tap"].str.lower().eq("val")].copy()
    return df


def val_metric_number(value):
    """Parse left-hand number from stored '0,xxxx ± ...' value, not regenerate metrics."""
    text = str(value).split("±")[0].strip().replace(",", ".")
    return float(text)


def group_ablation_val_means():
    """Summarize VAL-only ablation across frozen seeds; all source rows are included."""
    df = load_evidence("ablation_val")
    required={"cau_hinh","seed","AUPRC_val","AUROC_val"}
    if not required.issubset(df.columns):
        raise ValueError("Ablation VAL thiếu cột")
    return df.groupby("cau_hinh",as_index=False).agg(
        AUPRC_val_mean=("AUPRC_val","mean"),
        AUPRC_val_sd=("AUPRC_val","std"),
        AUROC_val_mean=("AUROC_val","mean"),
        n_seed=("seed","nunique")
    ).sort_values("cau_hinh").reset_index(drop=True)


def baseline_val_models():
    """Return exactly the four original baseline algorithms on frozen week-5 VAL."""
    models=['LogisticRegression','RandomForest','XGBoost','LightGBM']
    df=load_evidence('baseline')
    if not {'mo_hinh','auprc','auroc','tap'}.issubset(df.columns):
        raise ValueError('Thiếu dữ liệu cho bảng baseline')
    result=df.loc[df['mo_hinh'].isin(models)].copy()
    if result['mo_hinh'].duplicated().any() or set(result['mo_hinh'])!=set(models):
        raise ValueError('Phải có đúng một hàng VAL cho mỗi mô hình nền')
    if not result['tap'].str.lower().eq('val').all():
        raise ValueError('Không được trình bày các hàng TRAIN như VAL')
    result['mo_hinh']=pd.Categorical(result['mo_hinh'],categories=models,ordered=True)
    return result.sort_values('mo_hinh').reset_index(drop=True)


def load_stored_test_summary():
    """Read locked week-9 VAL–TEST aggregate table; NO raw data or inference."""
    path=EVIDENCE/'val_vs_test.csv'
    if not path.is_file():
        raise FileNotFoundError('Thiếu bảng tổng hợp VAL–TEST từ tuần 9.')
    df=pd.read_csv(path,encoding='utf-8-sig')
    requested={
        'AUPRC LR gộp (5 seed)':'Logistic Regression gộp',
        'AUPRC LightGBM gộp (5 seed)':'LightGBM gộp',
        'AUPRC Fusion (a) (5 seed)':'Fusion (a)',
        'AUPRC Fusion (b) (5 seed)':'Fusion (b)',
        'AUPRC Stacking (5 seed)':'Stacking',
    }
    results=df[df['muc'].isin(requested)].copy()
    if set(results['muc'])!=set(requested) or results['muc'].duplicated().any():
        raise ValueError('Bảng TEST đã lưu thiếu mô hình hoặc chứa dòng trùng.')
    results['Mô hình']=results['muc'].map(requested)
    results['AUPRC VAL (5 seed)']=results['validation'].astype(float).round(4)
    results['AUPRC TEST (5 seed)']=results['test'].astype(float).round(4)
    results['TEST − VAL']=results['test'].astype(float).sub(results['validation'].astype(float)).round(4)
    return results[['Mô hình','AUPRC VAL (5 seed)','AUPRC TEST (5 seed)','TEST − VAL']]
