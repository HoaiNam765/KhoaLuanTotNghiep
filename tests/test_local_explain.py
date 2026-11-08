import numpy as np
import pandas as pd
import pytest
from src.inference import ROOT,load_runtime,predict_case,prepare_features,predict_features
from src.local_explain import input_feature_groups,explain_preprocessed,explain_case


def test_grouping_26_to_43_exactly_once():
    bundle,*_=load_runtime()
    mapping=input_feature_groups(bundle)
    assert len(mapping)==26
    flattened=[feature for features in mapping.values() for feature in features]
    assert len(flattened)==43
    assert set(flattened)==set(bundle['feature_order'])
    assert 'diet_recall_missing' in mapping['DR1TKCAL']
    assert 'BPXOSY1_was_missing' in mapping['BPXOSY1']
    assert len(mapping['RIDRETH3'])==5
    assert len(mapping['SMOKE_STATUS'])==3
    assert len(mapping['GLYCEMIC_HX'])==2


def test_local_attribution_additive_and_model_is_unchanged():
    b,groups,weights,_,models=load_runtime()
    raw=pd.read_csv(ROOT/'tests/fixture_val_raw12.csv')
    ex=explain_preprocessed(raw.iloc[[1]],b,groups,weights,models,n_permutations=8)
    official,_=predict_features(raw.iloc[[1]],pd.read_csv(ROOT/'tests/fixture_val_scaled12.csv').iloc[[1]],groups,weights,models)
    assert np.isclose(ex['probability'],official,atol=1e-10)
    assert abs(ex['baseline']+sum(ex['contributions'].values())-official) <= 1e-9
    assert len(ex['contributions'])==26
    assert ex['reference_n']==12


def test_local_deterministic_by_fixed_seed():
    b,groups,weights,_,models=load_runtime()
    raw=pd.read_csv(ROOT/'tests/fixture_val_raw12.csv')
    a=explain_preprocessed(raw.iloc[[2]],b,groups,weights,models,n_permutations=8)
    c=explain_preprocessed(raw.iloc[[2]],b,groups,weights,models,n_permutations=8)
    assert a['contributions']==c['contributions']
    assert a['probability']==c['probability']


def test_explanation_matches_ui_case_probability_and_missing_indicators():
    b,*_=load_runtime()
    case={name:float(value) for name,value in zip(b['numeric_vars'],b['num_imputer'].statistics_)}
    case.update({'RIAGENDR':1,'BPQ020':1,'BPQ080':2,'PAQ650':2,'RIDRETH3':3,'SMOKE_STATUS':1,'GLYCEMIC_HX':1})
    case['BPXOSY1']=None
    case['DR1TKCAL']=None
    official=predict_case(case)
    local=explain_case(case,n_permutations=8)
    assert abs(local['probability']-official['probability']) < 1e-10
    assert np.isclose(local['baseline']+sum(local['contributions'].values()),official['probability'],atol=1e-9)


def test_bad_feature_order_rejected():
    b,groups,weights,_,models=load_runtime()
    raw=pd.read_csv(ROOT/'tests/fixture_val_raw12.csv')
    bad=raw.iloc[[0]].copy()[list(reversed(raw.columns))]
    with pytest.raises(ValueError,match='43 cột'):
        explain_preprocessed(bad,b,groups,weights,models,n_permutations=2)
    with pytest.raises(ValueError,match='Số hoán vị'):
        explain_preprocessed(raw.iloc[[0]],b,groups,weights,models,n_permutations=0)


def test_reference_synthetic_case_a_remains_5949_percent():
    case = {
        'RIDAGEYR':52,'BMXBMI':34.5,'BMXWAIST':112.0,'BMXHIP':110.0,
        'BPXOSY1':138.0,'BPXODI1':86.0,'RIAGENDR':1,'RIDRETH3':3,
        'LBXSASSI':45.0,'LBXSATSI':38.0,'LBXSGTSI':62.0,'LBXSTR':185.0,
        'LBDHDD':38.0,'LBXTC':210.0,'LBXSGL':118.0,'LBXGH':6.1,
        'BPQ020':1,'BPQ080':1,'GLYCEMIC_HX':1,'PAD680':480.0,
        'DR1TKCAL':None,'DR1TSUGR':None,'DR1TSFAT':None,'DR1TFIBE':None,
        'PAQ650':2,'SMOKE_STATUS':1,
    }
    pred = predict_case(case,'F1 OOF')
    expl = explain_case(case,24)
    assert round(pred['probability'] * 100,2) == 59.49
    assert abs(pred['probability']-expl['probability']) < 1e-10
    assert abs(expl['baseline']+sum(expl['contributions'].values())-expl['probability']) < 1e-9
