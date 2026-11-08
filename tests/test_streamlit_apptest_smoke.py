"""Widget smoke tests in a real Streamlit 1.66.1 environment, skipped if absent.
Not a substitute for browser/mobile screenshot acceptance.
"""
from pathlib import Path
import os
import hashlib
import pytest

if os.environ.get('RUN_APPTEST') != '1':
    pytest.skip('AppTest requires explicit opt-in with RUN_APPTEST=1 in a real Streamlit environment', allow_module_level=True)
streamlit = pytest.importorskip('streamlit')
from streamlit.testing.v1 import AppTest

ROOT=Path(__file__).resolve().parents[1]

def click_button(at, label):
    matches = [button for button in at.button if button.label == label]
    assert len(matches) == 1, f'Expected one button named {label!r}, found {len(matches)}'
    matches[0].click().run()

def test_open_intro_and_manual_prediction_without_uncaught_errors():
    at=AppTest.from_file(str(ROOT/'app/app.py'),default_timeout=40).run()
    assert not at.exception
    at.button(key='go_prediction').click().run()
    assert not at.exception
    click_button(at, 'Thử ca A · trên ngưỡng')
    at.button(key='predict_manual').click().run()
    assert not at.exception


def test_navigation_research_reclick_does_not_throw():
    at=AppTest.from_file(str(ROOT/'app/app.py'),default_timeout=40).run()
    at.button(key='go_research').click().run()
    assert not at.exception
    if at.get('segmented_control'):
        # Initial selection is allowed to be cleared; page must still show Tổng quan.
        at.get('segmented_control')[0].set_value(None).run()
        assert not at.exception


def test_manual_to_csv_to_row_detail_no_duplicate_key():
    from src.input_data import csv_template
    at=AppTest.from_file(str(ROOT/'app/app.py'),default_timeout=40).run()
    at.session_state['page']='Dự đoán'
    payload=csv_template()
    at.session_state['csv_payload']=payload
    at.session_state['csv_signature']=hashlib.sha256(payload).hexdigest()
    at.session_state['csv_filename']='mau.csv'
    at.run()
    assert not at.exception
    click_button(at, 'Dự đoán những dòng hợp lệ')
    assert not at.exception
    at.button(key='csv_choose_row').click().run()
    assert not at.exception
