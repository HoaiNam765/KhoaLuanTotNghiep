"""Pure session-state helpers for NAFLD Insight's Streamlit interface.

No persistence to filesystem or databases. Inputs and outputs only exist for the
current Streamlit session; none of these helpers load model or TEST artifacts.
"""
from __future__ import annotations


RESULT_KEYS = ('last_prediction', 'last_case', 'last_source', 'last_time', 'local_explanation')
BATCH_KEYS = ('batch_results', 'batch_cases', 'batch_signature')


def keep_draft(state, codes):
    """Mirror currently visible widget values to a durable, non-widget key."""
    saved = dict(state.get('draft_inputs') or {})
    for code in codes:
        widget_key = 'field_' + code
        if widget_key in state:
            saved[code] = state[widget_key]
    state['draft_inputs'] = saved
    return saved


def keep_field(state, code):
    saved = dict(state.get('draft_inputs') or {})
    widget_key = 'field_' + code
    if widget_key in state:
        saved[code] = state[widget_key]
    state['draft_inputs'] = saved


def restore_draft(state, numeric_codes, category_codes):
    """Rehydrate Streamlit keys before rendering widgets on returning to page."""
    saved = state.get('draft_inputs') or {}
    for code in numeric_codes:
        key = 'field_' + code
        if key not in state:
            state[key] = saved.get(code, '')
    for code in category_codes:
        key = 'field_' + code
        if key not in state:
            state[key] = saved.get(code)


def load_example(state, example, numeric_codes, category_codes):
    draft = {}
    for code in numeric_codes:
        value = example.get(code)
        draft[code] = '' if value is None else f'{value:g}'
    for code in category_codes:
        draft[code] = example.get(code)
    state['draft_inputs'] = draft
    for code, value in draft.items():
        state['field_' + code] = value
    clear_result(state)


def clear_result(state):
    """Discard output but preserve inputs and batch results."""
    for key in RESULT_KEYS:
        state.pop(key, None)


def new_case(state, numeric_codes, category_codes):
    """Clear manual inputs and output, without silently deleting CSV results."""
    clear_result(state)
    state['draft_inputs'] = {}
    for code in (*numeric_codes, *category_codes):
        state.pop('field_' + code, None)


def keep_csv_file(state, payload, filename):
    """Cache a CSV in current session across page navigation, not persist to disk."""
    import hashlib

    digest = hashlib.sha256(payload).hexdigest()
    if digest != state.get('csv_signature'):
        state.pop('confirm_csv_core_extrapolation', None)
        for key in BATCH_KEYS:
            state.pop(key, None)
        if str(state.get('last_source','')).startswith('CSV – xem từng dòng'):
            clear_result(state)
    state['csv_payload'] = payload
    state['csv_signature'] = digest
    state['csv_filename'] = filename
    return digest


def clear_csv_file(state):
    for key in ('csv_payload', 'csv_signature', 'csv_filename', *BATCH_KEYS, 'inspect_row', 'confirm_csv_core_extrapolation'):
        state.pop(key, None)
    if str(state.get('last_source','')).startswith('CSV – xem từng dòng'):
        clear_result(state)
    state['csv_upload_epoch'] = state.get('csv_upload_epoch', 0) + 1
