"""Regression checks for page navigation, reset actions and CSV persistence."""
from pathlib import Path

from src.input_data import NUMERIC_CODES, CATEGORY_CODES, EXAMPLE_A, validate_case
from src.ui_session import (
    keep_field, keep_draft, restore_draft, load_example, clear_result,
    new_case, keep_csv_file, clear_csv_file,
)


def test_draft_keeps_values_across_widget_cleanup_and_navigation():
    state = {}
    load_example(state, EXAMPLE_A, NUMERIC_CODES, CATEGORY_CODES)
    state['field_BMXWAIST'] = '107,5'
    keep_field(state, 'BMXWAIST')
    keep_draft(state, list(NUMERIC_CODES) + list(CATEGORY_CODES))
    for code in (*NUMERIC_CODES, *CATEGORY_CODES):
        state.pop('field_' + code, None)  # Streamlit cleans hidden widget keys
    restore_draft(state, NUMERIC_CODES, CATEGORY_CODES)
    assert state['field_BMXWAIST'] == '107,5'
    assert state['field_RIAGENDR'] == EXAMPLE_A['RIAGENDR']
    assert validate_case({c: state['field_' + c] for c in (*NUMERIC_CODES, *CATEGORY_CODES)})['BMXWAIST'] == 107.5


def test_clear_only_result_preserves_raw_form_values_and_explanation_cleared():
    state = {'field_RIDAGEYR': '52', 'draft_inputs': {'RIDAGEYR': '52'},
             'last_prediction': {'probability': .59}, 'last_case': {'RIDAGEYR': 52},
             'last_source': 'Nhập trực tiếp', 'last_time': 'today',
             'local_explanation': {'key': ('example',)}}
    clear_result(state)
    assert state['field_RIDAGEYR'] == '52'
    assert state['draft_inputs']['RIDAGEYR'] == '52'
    assert not any(k in state for k in ('last_prediction', 'last_case', 'last_source', 'last_time','local_explanation'))


def test_new_case_resets_form_and_result_without_dropping_research_or_csv():
    state = {'batch_results': [1], 'draft_inputs': {}, 'last_prediction': {'probability': .59}}
    load_example(state, EXAMPLE_A, NUMERIC_CODES, CATEGORY_CODES)
    new_case(state, NUMERIC_CODES, CATEGORY_CODES)
    assert state['draft_inputs'] == {}
    assert 'last_prediction' not in state
    assert 'field_RIDAGEYR' not in state
    assert state['batch_results'] == [1]
    restore_draft(state, NUMERIC_CODES, CATEGORY_CODES)
    assert state['field_RIDAGEYR'] == ''
    assert state['field_RIAGENDR'] is None


def test_csv_file_remains_available_during_navigation_and_unchanged_reupload():
    state = {}
    signature = keep_csv_file(state, b'col_a,col_b\n1,2', 'sample.csv')
    state['batch_signature'] = signature
    state['batch_results'] = [{'positive': True}]
    assert keep_csv_file(state, b'col_a,col_b\n1,2', 'sample.csv') == signature
    assert len(state['batch_results']) == 1
    assert state['csv_payload'] == b'col_a,col_b\n1,2'


def test_csv_file_replacement_invalidates_old_batch_but_preserves_manual_result():
    state = {'last_source': 'Nhập trực tiếp', 'last_prediction': {'probability': .23}}
    keep_csv_file(state, b'col\n1', 'first.csv')
    state['batch_results'] = [1]
    keep_csv_file(state, b'col\n2', 'second.csv')
    assert 'batch_results' not in state
    assert state['last_prediction'] == {'probability': .23}
    clear_csv_file(state)
    assert 'csv_payload' not in state
    assert state['csv_upload_epoch'] == 1


def test_app_has_explicit_actions_and_no_form_batching():
    code = (Path(__file__).resolve().parents[1] / 'app/app.py').read_text('utf-8')
    assert "key='clear_manual_result'" in code
    assert "key='new_manual_case'" in code
    assert "on_change=remember_field,args=(code,)" in code
    assert 'restore_draft(st.session_state, NUMERIC_CODES, CATEGORY_CODES)' in code
    assert "on_change=remember_csv_widget,args=(upload_key,)" in code
    assert "st.form('manual_clinical_data')" not in code
    assert "result=predict_case(case,DEFAULT_MODE)" in code
