"""Check number display and research summary without executing Streamlit or TEST."""
from src.ui_specs import number_input_kwargs
from src.research_evidence import baseline_val_models


def test_integer_fields_have_no_decimal_zeros():
    for code in ['RIDAGEYR','PAD680']:
        spec=number_input_kwargs(code)
        assert isinstance(spec['step'],int)
        assert spec['format']=='%d'
        assert spec['value'] is None
    assert number_input_kwargs('RIDAGEYR')['min_value']==18
    assert number_input_kwargs('RIDAGEYR')['max_value']==80


def test_float_measurements_show_no_trailing_decimal_zeros():
    spec=number_input_kwargs('BMXBMI')
    assert spec['format']=='%g'
    assert spec['value'] is None
    assert (spec['format'] % 35.0)=='35'
    assert (spec['format'] % 35.5)=='35.5'


def test_model_comparison_only_frozen_baseline_val():
    df=baseline_val_models()
    assert list(df['mo_hinh'].astype(str))==['LogisticRegression','RandomForest','XGBoost','LightGBM']
    assert len(df)==4
    assert df['tap'].str.lower().eq('val').all()
    assert df['auprc'].between(0,1).all()
    assert df['auroc'].between(0,1).all()
