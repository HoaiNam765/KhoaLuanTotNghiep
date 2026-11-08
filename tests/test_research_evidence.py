"""Frozen researcher dashboard sources: TRAIN CV / OOF / VAL only."""
import pytest
from src.research_evidence import FILES, load_evidence, val_metric_number, group_ablation_val_means


def test_research_evidence_allowlist_and_no_test_sources():
    assert len(FILES)==8
    for name, source in FILES.items():
        assert 'test' not in source.lower()
        df = load_evidence(name)
        assert len(df)>0
        assert not any('test' in c.lower() for c in df.columns)
    with pytest.raises(KeyError):
        load_evidence('../TEST')


def test_baseline_view_only_val():
    df=load_evidence('baseline')
    assert df['tap'].eq('val').all()
    assert len(df)==5
    assert {'LogisticRegression','RandomForest','XGBoost','LightGBM'}.issubset(set(df['mo_hinh']))


def test_fusion_val_numbers_from_saved_file():
    df=load_evidence('comparison_val')
    fusion = df.loc[(df['Mô hình']=='Fusion (b)') & (df['Ngưỡng']=='F1 (từ OOF)')]
    assert len(fusion)==1
    assert abs(val_metric_number(fusion.iloc[0]['AUPRC'])-0.6795)<1e-4
    assert abs(val_metric_number(fusion.iloc[0]['AUROC'])-0.8376)<1e-4


def test_fusion_ablation_val_has_all_frozen_seeds():
    df=group_ablation_val_means()
    assert len(df)==4
    assert set(df['n_seed'])=={5}
    assert df['AUPRC_val_mean'].between(0,1).all()
