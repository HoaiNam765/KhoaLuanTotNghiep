"""Tests for usability layer; no TEST access or model refitting."""
import csv
import io
import math

import pytest

from src.input_data import (
    ALL_CODES,CATEGORY_CODES,NUMERIC_CODES,EXAMPLE_A,EXAMPLE_B,
    InputError,batch_predict,csv_template,parse_csv_bytes,validate_case,
)
from src.inference import load_runtime,predict_case


def test_26_input_variables_exactly():
    b,*_=load_runtime()
    assert len(ALL_CODES)==26
    assert set(ALL_CODES)==set(b['numeric_vars'])|set(b['binary_mappings'])|set(b['multi_categorical_vars'])
    assert len(set(ALL_CODES))==26


def test_examples_match_original_frozen_artifacts():
    one=predict_case(validate_case(EXAMPLE_A),'F1 OOF')
    two=predict_case(validate_case(EXAMPLE_B),'F1 OOF')
    assert abs(one['probability']-0.594926546959962)<1e-8
    assert abs(two['probability']-0.023197581277779444)<1e-8
    assert one['positive'] and not two['positive']


def test_csv_template_validates_two_fictional_rows():
    data=csv_template()
    assert data.startswith(b'\xef\xbb\xbf')
    parsed=parse_csv_bytes(data)
    assert len(parsed.rows)==2
    assert not parsed.errors
    assert not parsed.extra_columns
    for case,example in zip(parsed.rows,(EXAMPLE_A,EXAMPLE_B)):
        assert case==validate_case(example)


def test_batch_inference_matches_manual_without_change_to_threshold():
    parsed=parse_csv_bytes(csv_template())
    records,cases=batch_predict(parsed,predict_case)
    assert [r['Kết luận'] for r in records]==['Trên ngưỡng nguy cơ nghiên cứu','Dưới ngưỡng nguy cơ nghiên cứu']
    assert records[0]['Xác suất (%)']==59.49
    assert records[1]['Xác suất (%)']==2.32
    assert set(cases)=={2,3}
    assert all(result['mode']=='F1 OOF' for case,result in cases.values())
    assert all('RIDAGEYR' not in r for r in records)  # No raw input data in download


def test_missing_numeric_not_interpreted_as_zero():
    a=dict(EXAMPLE_A)
    assert validate_case(a)['DR1TKCAL'] is None
    a['DR1TKCAL']='0'
    assert validate_case(a)['DR1TKCAL']==0
    a['BMXBMI']='34,5'
    assert validate_case(a)['BMXBMI']==34.5


def test_invalid_age_and_category_rejected():
    for age in (None,'','17','81','abc','52.5','nan','inf'):
        raw=dict(EXAMPLE_A,RIDAGEYR=age)
        with pytest.raises(InputError):validate_case(raw)
    with pytest.raises(InputError):validate_case(dict(EXAMPLE_A,RIAGENDR=None))
    with pytest.raises(InputError):validate_case(dict(EXAMPLE_A,RIDRETH3='999'))


def test_prevent_invalid_numeric_and_infinity():
    for bad in ('-10','inf','NaNNotNumber','100001','1e309'):
        with pytest.raises(InputError):validate_case(dict(EXAMPLE_A,BMXBMI=bad))
    with pytest.raises(InputError):validate_case(dict(EXAMPLE_A,PAD680='200,3'))


def test_csv_supports_excel_semicolon_and_decimal_comma():
    text=csv_template().decode('utf-8-sig')
    reader=csv.DictReader(io.StringIO(text))
    out=io.StringIO()
    writer=csv.DictWriter(out,fieldnames=ALL_CODES,delimiter=';')
    writer.writeheader()
    for row in reader:
        row['BMXBMI']=row['BMXBMI'].replace('.',',')
        writer.writerow(row)
    parsed=parse_csv_bytes(out.getvalue().encode('utf-8'))
    assert len(parsed.rows)==2 and not parsed.errors
    assert parsed.rows[0]['BMXBMI']==34.5


def test_csv_invalid_rows_are_reported_not_predicted():
    text=csv_template().decode('utf-8-sig')
    reader=list(csv.DictReader(io.StringIO(text)))
    reader[1]['RIAGENDR']='999'
    out=io.StringIO()
    w=csv.DictWriter(out,fieldnames=ALL_CODES)
    w.writeheader();w.writerows(reader)
    parsed=parse_csv_bytes(out.getvalue().encode('utf-8'))
    assert set(parsed.errors)=={3}
    records,cases=batch_predict(parsed,predict_case)
    assert records[1]['Kết luận']=='Không hợp lệ'
    assert set(cases)=={2}


def test_csv_bad_schema_and_max_rows_and_size():
    data=csv_template().decode('utf-8-sig')
    with pytest.raises(InputError,match='thiếu cột'):
        parse_csv_bytes(data.replace('RIAGENDR','RIAGENDER').encode())
    with pytest.raises(InputError,match='1 MB'):
        parse_csv_bytes(b'a'*1_000_001)
    lines=data.splitlines()
    excessive=('\n'.join([lines[0]]+[lines[1]]*101)).encode('utf-8')
    with pytest.raises(InputError,match='100'):
        parse_csv_bytes(excessive)


def test_csv_rejects_header_duplicate_and_mismatched_columns():
    data=csv_template().decode('utf-8-sig')
    duplicate=data.replace('RIDAGEYR,BMXBMI,','RIDAGEYR,RIDAGEYR,',1)
    with pytest.raises(InputError,match='trùng'):
        parse_csv_bytes(duplicate.encode('utf-8'))
    broken=data.splitlines()
    broken[1]+=',42'
    with pytest.raises(InputError,match='số ô'):
        parse_csv_bytes('\n'.join(broken).encode('utf-8'))


def test_app_user_interface_no_manual_threshold_selection():
    from pathlib import Path
    app=(Path(__file__).resolve().parents[1]/'app'/'app.py').read_text(encoding='utf8')
    assert "result=predict_case(case,DEFAULT_MODE)" in app
    assert "records,cases=batch_predict(parsed,predict_case)" in app
    assert "st.radio('Chế độ ngưỡng'" not in app
    assert 'Đây là phân loại của mô hình nghiên cứu' in app
    assert "st.file_uploader('Chọn tệp CSV UTF-8'" in app
