"""Assertions for 03/11/2026 fixes. Runs offline; never reads TEST observations."""
import csv
import hashlib
import io
import json
from pathlib import Path

import pytest

from src.inference import ROOT, load_runtime, predict_case, integrity
from src.input_data import EXAMPLE_A, EXAMPLE_B, InputError, validate_case, input_warnings, core_measurement_extrapolations, parse_csv_bytes, csv_template, batch_predict
from src.research_evidence import load_stored_test_summary
from src.local_explain import VAL_BACKGROUND
from src.ui_session import keep_csv_file, clear_csv_file


def test_locked_predictions_unchanged():
    a=predict_case(validate_case(EXAMPLE_A));b=predict_case(validate_case(EXAMPLE_B))
    assert a['probability']==pytest.approx(0.594926546959962,abs=1e-12)
    assert b['probability']==pytest.approx(0.023197581277779444,abs=1e-12)
    assert a['threshold']==pytest.approx(0.3315983622272108,abs=1e-15)

@pytest.mark.parametrize('changed', [
    {'BMXWAIST': '1,12'}, {'BMXWAIST':'0'}, {'BMXWAIST':'11200'},
    {'BMXBMI':'0'}, {'BMXBMI':'345'}, {'BMXBMI':'5000'},
    {'BPXOSY1':'80','BPXODI1':'140'}, {'LBXGH':'61'},
    {'PAD680':'2000'}, {'LBXSTR':'1,200'}, {'LBXSATSI':'1.000'},
    {'LBXSGTSI':'1,192'}, {'DR1TKCAL':'1,800'},
])
def test_invalid_obvious_input_rejected(changed):
    with pytest.raises(InputError):validate_case({**EXAMPLE_A,**changed})



def test_core_body_measurements_outside_train_are_flagged_for_confirmation():
    case = validate_case({**EXAMPLE_A, 'BMXBMI': '12', 'BMXWAIST': '44'})
    flags = core_measurement_extrapolations(case)
    assert {item[0] for item in flags} == {'BMXBMI', 'BMXWAIST'}
    warnings = input_warnings(case)
    assert any('ngoài khoảng quan sát trong TRAIN' in item and 'ngoại suy' in item for item in warnings)


def test_unambiguous_decimal_values_remain_supported():
    case = validate_case({**EXAMPLE_A, 'LBXSATSI': '1,2', 'DR1TKCAL': '1800'})
    assert case['LBXSATSI'] == pytest.approx(1.2)
    assert case['DR1TKCAL'] == pytest.approx(1800)


@pytest.mark.parametrize('code,text,expected', [
    ('DR1TSFAT', '39.178', 39.178), ('DR1TSFAT', '4,802', 4.802),
    ('DR1TSUGR', '90.965', 90.965), ('DR1TFIBE', '14.300', 14.3),
])
def test_nhanes_gram_values_with_three_decimals_are_accepted(code, text, expected):
    # NHANES ghi khẩu phần (gam) tới 3 chữ số lẻ; đây là số thập phân, không phải dấu hàng nghìn.
    case = validate_case({**EXAMPLE_A, code: text})
    assert case[code] == pytest.approx(expected)
    assert predict_case(case)['probability'] == pytest.approx(0.594926546959962, abs=1e-12)


def test_csv_row_with_three_decimal_saturated_fat_is_valid():
    lines = csv_template().decode('utf-8-sig').splitlines()
    header = lines[0].split(',')
    row = lines[1].split(',')
    row[header.index('DR1TSFAT')] = '24.344'
    parsed = parse_csv_bytes('\n'.join([lines[0], ','.join(row)]).encode('utf8'))
    assert parsed.errors == {}
    assert parsed.rows[0]['DR1TSFAT'] == pytest.approx(24.344)

def test_reserved_survey_codes_treated_as_missing_not_9999_minutes():
    assert validate_case({**EXAMPLE_A,'PAD680':'7777'})['PAD680'] is None
    assert validate_case({**EXAMPLE_A,'PAD680':'9999'})['PAD680'] is None


def test_optional_category_missing_is_imputed_by_original_pipeline():
    case=validate_case({**EXAMPLE_A,'BPQ020':None,'BPQ080':'Không rõ','PAQ650':None,'GLYCEMIC_HX':None,'SMOKE_STATUS':None})
    assert case['BPQ020'] is None
    assert 0 <= predict_case(case)['probability'] <= 1
    with pytest.raises(InputError):validate_case({**EXAMPLE_A,'RIAGENDR':None})


def test_warnings_for_train_extrapolation_and_mmol_l_not_diagnosis():
    case=validate_case({**EXAMPLE_A,'LBXSGL':'4,7','BMXBMI':'90'})
    warnings=input_warnings(case)
    assert any('mg/dL' in x and 'mmol/L' in x for x in warnings)
    assert any('TRAIN' in x for x in warnings)


def test_missing_body_measurements_are_cautioned():
    case=validate_case({**EXAMPLE_A,'BMXBMI':None,'BMXWAIST':None,'BMXHIP':None})
    assert any('CẢNH BÁO MẠNH' in x for x in input_warnings(case))


def test_csv_blank_line_keeps_actual_file_line_number():
    text=csv_template().decode('utf-8-sig').splitlines()
    mutated='\n'.join([text[0],text[1],'',text[2].replace('30,','17,',1)])
    parsed=parse_csv_bytes(mutated.encode('utf8'))
    assert parsed.row_numbers == [2,4]
    assert set(parsed.errors)=={4}
    rec,cases=batch_predict(parsed,predict_case)
    assert rec[1]['Dòng CSV']==4
    assert cases.keys()=={2}


def test_csv_results_export_has_model_and_threshold_no_clinical_input():
    parsed=parse_csv_bytes(csv_template())
    records,cases=batch_predict(parsed,predict_case)
    assert records[0]['Ngưỡng F1 OOF (%)']==33.16
    assert records[0]['Mô hình']=='Fusion (b) seed 42'
    assert 'BMXBMI' not in records[0]


def test_test_summary_is_read_only_and_precise():
    df=load_stored_test_summary()
    assert len(df)==5
    fusion=df.loc[df['Mô hình']=='Fusion (b)'].iloc[0]
    lgbm=df.loc[df['Mô hình']=='LightGBM gộp'].iloc[0]
    assert fusion['AUPRC TEST (5 seed)']==pytest.approx(0.6881)
    assert lgbm['AUPRC TEST (5 seed)']==pytest.approx(0.6910)


def test_manifest_protects_models_json_and_background(tmp_path,monkeypatch):
    import src.inference as inf
    man=json.loads((ROOT/'artifacts/manifest.json').read_text(encoding='utf8'))['sha256']
    for rel in ('artifacts/groups.json','artifacts/weights.json','artifacts/thresholds.json','artifacts/local_explain_background_val12.csv'):
        assert man[rel]==hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()
    # Copy only the locked files; modify one JSON, then ensure integrity() fails.
    for rel in man:
        dest=tmp_path/rel;dest.parent.mkdir(parents=True,exist_ok=True)
        dest.write_bytes((ROOT/rel).read_bytes())
    dest=tmp_path/'artifacts/thresholds.json'
    dest.write_bytes(dest.read_bytes()+b' ')
    (tmp_path/'artifacts/manifest.json').write_text(json.dumps({'sha256':man}),encoding='utf8')
    monkeypatch.setattr(inf,'ROOT',tmp_path)
    monkeypatch.setattr(inf,'ART',tmp_path/'artifacts')
    with pytest.raises(RuntimeError,match='thresholds.json'):
        integrity()


def test_local_explanation_does_not_require_tests_folder():
    assert VAL_BACKGROUND.is_file()
    assert VAL_BACKGROUND.parent.name == 'artifacts'
    assert len(list(csv.DictReader(VAL_BACKGROUND.open(encoding='utf8'))))==12




def test_csv_extrapolation_acknowledgement_resets_for_new_file():
    state={'csv_signature':'old','confirm_csv_core_extrapolation':True}
    keep_csv_file(state,b'new csv bytes','new.csv')
    assert 'confirm_csv_core_extrapolation' not in state


def test_app_places_input_warnings_before_probability_and_gates_extrapolation():
    source=(ROOT/'app/app.py').read_text(encoding='utf8')
    warning_at=source.index('for warning in input_warnings(case):')
    probability_at=source.index('<div class="number">{probability*100:.2f}%</div>')
    assert warning_at < probability_at
    assert "confirm_core_extrapolation" in source
    assert "confirm_csv_core_extrapolation" in source
    assert "disabled=bool(extrapolated_rows and not confirm_csv_extrapolation)" in source

def test_csv_session_cleanup_with_numbered_source():
    state={'last_source':'CSV – xem từng dòng 3','last_prediction':{'probability':0.4},'last_case':{}}
    keep_csv_file(state,b'row\n1','abc.csv')
    clear_csv_file(state)
    assert 'last_prediction' not in state


def test_ui_no_duplicate_button_key_and_research_fallback():
    s=(ROOT/'app/app.py').read_text(encoding='utf8')
    assert "key=f'compute_explain_{context}'" in s
    assert "key=f'local_shap_chart_{context}'" in s
    assert "or 'Tổng quan'" in s
    assert 'stack=False' in s
    assert 'st.rerun()' in s
