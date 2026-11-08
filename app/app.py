"""NAFLD Insight | Accessible two-audience Streamlit interface.

Clinical data stay in the current Streamlit session. No database or retraining.
Displays frozen TRAIN CV / OOF / VAL data and read-only TEST aggregate tables.
"""
from __future__ import annotations

from datetime import datetime
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src.inference import ROOT, load_runtime, predict_case
from src.input_data import (
    ALL_CODES, CATEGORY_CODES, CHOICES, CATEGORY_HELP, EXAMPLE_A, EXAMPLE_B,
    GROUP_CODES, GROUP_TITLES, NUMERIC_CODES, NUMERIC_HELP,
    OPTIONAL_CATEGORIES, FIELD_NAMES, input_warnings, core_measurement_extrapolations,
    InputError, batch_predict, csv_template, csv_columns_guide, parse_csv_bytes, validate_case,
)
from src.local_explain import explain_case, input_feature_groups
from src.branding import image_to_data_uri, load_brand_image
from src.ui_session import (
    keep_draft, keep_field, restore_draft, load_example, clear_result,
    new_case, keep_csv_file, clear_csv_file,
)
from src.research_evidence import (
    SOURCE_DESCRIPTIONS, baseline_val_models, group_ablation_val_means,
    load_evidence, val_metric_number, load_stored_test_summary,
)

st.set_page_config(page_title='NAFLD Insight | Dự đoán và giải thích', page_icon=':material/monitor_heart:', layout='wide', initial_sidebar_state='collapsed')

# Semantic design tokens: calm, editorial medical research; no gradients/emoji/inflated color.
CSS = """
<style>
:root{--page:#f5f7f5;--card:#ffffff;--ink:#172c32;--muted:#51666a;--line:#dce5e1;--accent:#176a72;--accent-soft:#eaf4f1;--alert:#895023;--alert-soft:#fff4e9;--good:#326447}
html{font-size:16px}body,[class*="css"]{font-family:system-ui,-apple-system,"Segoe UI",Arial,sans-serif}
[data-testid="stAppViewContainer"]{background:var(--page);color:var(--ink)}
[data-testid="stHeader"]{background:var(--page)}
[data-testid="stSidebar"]{display:none}
.main .block-container{max-width:1280px;padding:1.1rem 2rem 4.5rem}
h1,h2,h3,h4{color:var(--ink)!important;letter-spacing:-.025em!important}
h1{font-size:clamp(2rem,3.5vw,2.8rem)!important;font-weight:740!important}
h2{font-size:1.52rem!important}h3{font-size:1.2rem!important}
p,li,[data-testid="stMarkdownContainer"]{line-height:1.65}
[data-testid="stCaptionContainer"]{color:var(--muted)}
[data-testid="stTabs"] [role="tablist"]{gap:0.55rem;flex-wrap:wrap;border-bottom:1px solid var(--line)}
[data-testid="stTabs"] [role="tab"]{padding:0.65rem 1.05rem;min-height:44px;font-size:0.95rem}
[data-testid="stTabs"] [aria-selected="true"]{color:var(--accent)}
[data-testid="stVerticalBlockBorderWrapper"]:has([data-testid="stForm"]){border-radius:14px}
[data-testid="stForm"]{border-radius:14px;background:#fff;border:1px solid var(--line);padding:22px}
[data-testid="stMetric"]{background:#fff;border:1px solid var(--line);border-radius:12px;padding:16px 20px}
[data-testid="stMetricValue"]{color:var(--ink)}
[data-testid="stDataFrame"]{border-radius:10px;overflow:hidden}
[data-testid="stFileUploader"]{padding:4px 0}
[data-testid="stRadio"] label{cursor:pointer}
[data-testid="stRadio"] [role="radiogroup"]{gap:0.65rem}
[data-testid="stSidebar"] [data-testid="stRadio"] label{padding:4px 3px}
[data-testid="stFormSubmitButton"] button,button[kind="primary"]{background:var(--accent)!important;border:1px solid var(--accent)!important;color:white!important;font-weight:700;min-height:46px}
button[kind="primary"]:hover,[data-testid="stFormSubmitButton"] button:hover{background:#10545a!important}
button[kind="secondary"]{border-color:#b8ccca;color:var(--ink);min-height:43px}
button:focus-visible,input:focus-visible,[role="tab"]:focus-visible,[role="radio"]:focus-visible{outline:3px solid #b38935!important;outline-offset:2px}
[data-testid="stTextInput"] input,[data-testid="stNumberInput"] input{min-height:44px}
[data-testid="stExpander"]{border:1px solid var(--line)!important;border-radius:12px;background:#fff;margin-bottom:12px}
[data-testid="stExpander"] summary{min-height:50px}
[data-testid="stForm"] [role="radiogroup"]>label{border:1px solid #dfe8e5;background:#fcfdfc;border-radius:8px;padding:7px 11px;min-height:39px}
[data-testid="stForm"] [role="radiogroup"]>label:has(input:checked){border-color:var(--accent);background:var(--accent-soft)}
.small-cap{color:var(--accent);font-size:0.78rem;font-weight:750;letter-spacing:.11em;text-transform:uppercase}
.intro{padding:5px 0 18px;border-bottom:1px solid var(--line);margin-bottom:24px}
.intro h1{margin:4px 0 8px}.intro p{margin:0;max-width:730px;color:var(--muted);font-size:1.03rem}
.stat{background:#fff;border:1px solid var(--line);border-radius:12px;padding:17px 19px;margin:0 0 12px}
.stat strong{display:block;font-size:1.55rem;letter-spacing:-.035em;color:var(--ink)}
.stat span{color:var(--muted);font-size:.88rem}
.step{background:#fff;border:1px solid var(--line);border-radius:12px;padding:20px;min-height:140px;margin:0 0 12px}
.step-num{color:var(--accent);font-weight:750;font-size:.84rem;letter-spacing:.08em}
.step-title{font-size:1.04rem;font-weight:725;color:var(--ink);margin:7px 0 4px}
.step-text{color:var(--muted);font-size:.94rem;line-height:1.58}
.notice{background:var(--accent-soft);border-left:3px solid var(--accent);border-radius:6px;padding:14px 17px;color:#23474b;margin:12px 0 18px;line-height:1.65}
.caution{background:var(--alert-soft);border-left:3px solid #ae7438;border-radius:6px;padding:14px 17px;color:#604220;margin:12px 0 18px;line-height:1.65}
.result{background:#fff;border:1px solid var(--line);border-radius:16px;padding:23px;margin:18px 0}
.result .eyebrow{font-weight:700;color:var(--muted);font-size:.82rem;letter-spacing:.035em}
.result .number{font-weight:750;letter-spacing:-.04em;font-size:clamp(2.4rem,6vw,3.4rem);color:var(--ink);margin:7px 0}
.result .status{color:#815020;font-weight:725;font-size:1.08rem}
.result .negative{color:var(--good)}
.result .meter{height:9px;background:#e6eeeb;border-radius:20px;overflow:hidden;margin:16px 0}
.result .meter span{display:block;height:100%;background:var(--accent);border-radius:20px}
.muted-small{color:var(--muted);font-size:.88rem;line-height:1.7}
.source-line{color:var(--muted);font-size:.85rem;border-left:2px solid #b6cac6;padding-left:12px;margin:10px 0 18px}
.footer{margin-top:32px;border-top:1px solid var(--line);padding-top:16px;color:var(--muted);font-size:.84rem}
/* Distinct, genuinely horizontal site navigation: four equal cards. */
.site-head{display:flex;align-items:center;gap:14px;min-height:74px;padding:10px 0 8px}
.site-mark{width:52px;height:52px;border-radius:14px;display:flex;align-items:center;justify-content:center;background:#146975;flex:0 0 52px;overflow:hidden}
.site-mark img{object-fit:contain;max-width:100%;max-height:100%;background:#fff}
.site-wordmark{font-weight:780;letter-spacing:-.045em;color:var(--ink);font-size:1.55rem;line-height:1.15}
.site-submark{color:var(--muted);font-size:.9rem;margin-top:5px}
.site-overline{color:#4e7474;letter-spacing:.08em;text-transform:uppercase;font-size:.72rem;font-weight:730}
div[class*="st-key-nav_"] button{display:flex!important;flex-direction:column!important;justify-content:center!important;align-items:center!important;gap:4px!important;border:1px solid var(--line)!important;border-radius:14px!important;min-height:78px!important;background:#fff!important;color:var(--ink)!important;font-weight:650!important;font-size:1rem!important;box-shadow:0 1px 2px #1a36380a!important;transition:background-color .16s,border-color .16s!important}
div[class*="st-key-nav_"] button:hover{background:#eff6f3!important;border-color:#94bcb6!important}
div[class*="st-key-nav_"] button:focus-visible{outline:3px solid #b38935!important}
div[class*="st-key-nav_active_"] button{background:var(--accent-soft)!important;border:1.8px solid var(--accent)!important;color:#12545b!important;box-shadow:inset 0 -3px var(--accent)!important}
div[class*="st-key-nav_"] button [data-testid="stIconMaterial"],div[class*="st-key-nav_"] button .material-symbols-rounded{font-size:1.5rem!important;line-height:1.25}
.hero-panel{background:#edf4f1;border:1px solid #d9e7e2;border-radius:20px;padding:28px 30px;margin:16px 0 24px}
.hero-title{font-size:clamp(1.85rem,3.5vw,2.65rem);font-weight:760;line-height:1.22;letter-spacing:-.04em;color:var(--ink);max-width:650px;margin:6px 0 11px}
.hero-desc{font-size:1.03rem;line-height:1.75;color:var(--muted);max-width:650px}
.hero-tag{color:#176a72;font-weight:740;font-size:.76rem;text-transform:uppercase;letter-spacing:.1em}
.instruction-box{border:1px solid var(--line);background:#fff;border-radius:13px;padding:19px;margin-bottom:15px}
.instruction-box strong{color:var(--ink)}.instruction-box p{color:var(--muted);font-size:.93rem;margin:8px 0 0}
.screen-section{border-left:3px solid var(--accent);padding:3px 0 3px 13px;margin:17px 0 19px}
.screen-section h3{margin:0 0 4px!important}.screen-section p{color:var(--muted);margin:0;font-size:.92rem}
[data-testid="stFileUploader"] section{background:#fbfcfb;border:1px dashed #b9d0c9;border-radius:10px}
/* Balanced cards and stable top alignment on desktop. */
.hero-panel,.hero-aside{box-sizing:border-box;min-height:286px;height:286px;margin:9px 0 18px;display:flex;flex-direction:column;justify-content:center}
.hero-panel{background:#edf4f1;padding:30px 34px}
.hero-aside{border:1px solid var(--line);border-radius:20px;background:#fff;padding:26px 28px}
.hero-aside h3{margin:12px 0 8px!important;font-size:1.24rem!important}
.hero-aside p{margin:6px 0 8px;font-size:.95rem;line-height:1.65;color:var(--muted)}
.hero-aside p b{color:var(--ink)}
.hero-with-image{padding:0;overflow:hidden}
.hero-with-image img{display:block;width:100%;height:286px;object-fit:cover}
.stat{min-height:96px;display:flex;flex-direction:column;justify-content:center}
.step{min-height:170px;display:flex;flex-direction:column;justify-content:flex-start}
.group-card{background:#fff;border:1px solid var(--line);border-radius:12px;padding:21px 22px;min-height:172px;margin-bottom:14px}
.group-card strong{display:block;color:var(--ink);font-size:1rem;margin-top:7px}
.group-card p{color:var(--muted);font-size:.93rem;margin:10px 0 0;line-height:1.6}
[data-testid="stVerticalBlockBorderWrapper"]:has(div[class*="st-key-predict_manual"]){background:white;border-radius:14px}
@media (max-width:1100px){.hero-panel,.hero-aside{height:auto;min-height:286px}}
@media (max-width:760px){.site-wordmark{font-size:1.22rem}.site-submark{font-size:.77rem}.site-mark{width:44px;height:44px;flex-basis:44px}.hero-panel{padding:21px 19px}div[class*="st-key-nav_"] button{font-size:.82rem!important;min-height:48px!important} .main .block-container{padding:1.1rem 0.9rem 3rem}.hero-panel,.hero-aside{height:auto;min-height:0;margin:2px 0 8px}.hero-with-image img{height:220px}.step,.group-card{min-height:0}}

@media(max-width:700px){.main .block-container{padding:1.1rem 0.9rem 3rem} [data-testid="stForm"]{padding:13px}h1{font-size:2rem!important}}
@media(prefers-reduced-motion:reduce){*,*::before,*::after{animation:none!important;transition:none!important}}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# Hard-coded brand image paths: change filenames here (or replace the PNG files).
# Only repository-local static images are used. No runtime image upload controls.
BRAND_ASSETS = ROOT_DIR / 'app' / 'assets'
BRAND_IMAGE_PATHS = {
    'logo': BRAND_ASSETS / 'logo.png',         # Header (square, transparent suggested)
    'cover': BRAND_ASSETS / 'cover.png',       # Introduction hero (landscape)
    'research': BRAND_ASSETS / 'research.png', # Research overview (landscape)
}
NAV_ITEMS = (
    ('Giới thiệu', 'intro', ':material/home:'),
    ('Dự đoán', 'prediction', ':material/assignment:'),
    ('Giải thích', 'explain', ':material/menu_book:'),
    ('Nghiên cứu', 'research', ':material/monitoring:'),
)


def brand_image_bytes(kind):
    """Read a fixed image from app/assets, never from browser/session uploads."""
    return load_brand_image(BRAND_IMAGE_PATHS[kind], ROOT_DIR)


def site_header():
    current_page = st.session_state.get('page', 'Giới thiệu')
    logo = brand_image_bytes('logo')
    if logo is not None:
        mark = '<img alt="Logo NAFLD Insight" src="' + image_to_data_uri(logo) + '" />'
    else:
        # Original built-in icon remains available until app/assets/logo.png exists.
        mark = """<svg width="30" height="30" viewBox="0 0 32 32" aria-hidden="true" fill="none"><rect x="5" y="6" width="22" height="20" rx="5" stroke="white" stroke-width="2"/><path d="M9 17h4l3-6 4 11 3-5" stroke="white" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/></svg>"""
    st.markdown('<div class="site-head"><div class="site-mark">'+mark+'</div><div><div class="site-wordmark">NAFLD Insight</div><div class="site-submark">Dự đoán nguy cơ gan nhiễm mỡ không do rượu · Minh bạch bằng chứng nghiên cứu</div></div></div>', unsafe_allow_html=True)
    navbar = st.columns(4, gap='small')
    for col, (label, slug, icon) in zip(navbar, NAV_ITEMS):
        with col:
            with st.container(key='nav_' + ('active_' if label == current_page else '') + slug):
                st.button(label, icon=icon, key='go_'+slug, width='stretch',
                          on_click=select_page,args=(label,))
    st.markdown('<div style="height:12px"></div>',unsafe_allow_html=True)


def select_page(target):
    keep_draft(st.session_state, ALL_CODES)
    st.session_state['page'] = target


@st.cache_resource(show_spinner='Đang kiểm tra mô hình đã khóa…')
def runtime():
    return load_runtime()

try:
    preprocessor, groups, weights, thresholds, models = runtime()
except Exception as exc:
    st.error('Không thể xác minh mô hình đã khóa. Tính năng dự đoán đã được dừng để bảo vệ tính toàn vẹn kết quả.')
    st.caption('Vui lòng kiểm tra các tệp trong thư mục artifacts/ hoặc liên hệ nhóm nghiên cứu; chi tiết lỗi được ghi trong terminal chạy ứng dụng.')
    st.stop()

@st.cache_data(show_spinner=False)
def metadata():
    try:
        info = pd.read_csv(ROOT/'resource/ten_bien_don_vi.csv', encoding='utf-8-sig')
        return {r.bien_goc: (str(r.ten_bien), '' if pd.isna(r.don_vi) else str(r.don_vi)) for r in info.itertuples()}
    except (OSError, ValueError, KeyError, AttributeError) as exc:
        st.error('Thiếu hoặc hỏng bảng thông tin 26 biến. Vui lòng khôi phục thư mục resource và khởi động lại ứng dụng.')
        st.stop()

LABELS = metadata()
GROUP_DESCRIPTIONS = {
    'G1':'Tuổi, giới tính, nhóm dân tộc NHANES, chỉ số cơ thể và huyết áp.',
    'G2':'Các xét nghiệm máu thường gặp, như AST, ALT, GGT, triglyceride và HbA1c.',
    'G3':'Thông tin về tăng huyết áp, cholesterol và đường huyết trước đây.',
    'G4':'Vận động, thời gian ngồi, hút thuốc và khẩu phần một ngày.'
}
GROUP_LABELS = {'G1':'Đặc điểm cơ thể', 'G2':'Xét nghiệm máu',
                'G3':'Tiền sử sức khỏe', 'G4':'Lối sống và ăn uống'}
COLOR_PRIMARY='#176a72'
COLOR_SECONDARY='#9f7450'
DEFAULT_MODE = 'F1 OOF'


def heading(kicker, title, subtitle):
    st.markdown(f'<div class="intro"><div class="small-cap">{kicker}</div><h1>{title}</h1><p>{subtitle}</p></div>', unsafe_allow_html=True)


def columns_stats(items):
    for col, (value, label) in zip(st.columns(len(items)), items):
        col.markdown(f'<div class="stat"><strong>{value}</strong><span>{label}</span></div>', unsafe_allow_html=True)


def step_card(index, title, description):
    st.markdown(f'<div class="step"><div class="step-num">BƯỚC {index}</div><div class="step-title">{title}</div><div class="step-text">{description}</div></div>', unsafe_allow_html=True)


def mark_source(key):
    st.markdown(f'<div class="source-line">Nguồn đối chiếu: {SOURCE_DESCRIPTIONS[key]}</div>', unsafe_allow_html=True)


def take_to_prediction():
    select_page('Dự đoán')


def take_to_research():
    select_page('Nghiên cứu')


def load_demo(example):
    """Replace both the visible form and durable draft with a synthetic case."""
    st.session_state.pop('confirm_core_extrapolation', None)
    load_example(st.session_state,example,NUMERIC_CODES,CATEGORY_CODES)


def remember_field(code):
    keep_field(st.session_state, code)
    st.session_state.pop('confirm_core_extrapolation', None)
    st.session_state.pop('form_error',None)
    st.session_state.pop('error_groups',None)


def clear_last_result():
    keep_draft(st.session_state, ALL_CODES)
    clear_result(st.session_state)


def start_new_case():
    st.session_state.pop('confirm_core_extrapolation', None)
    new_case(st.session_state, NUMERIC_CODES, CATEGORY_CODES)


def remember_csv_widget(upload_key):
    uploaded=st.session_state.get(upload_key)
    if uploaded is not None:
        keep_csv_file(st.session_state,uploaded.getvalue(),uploaded.name)


def discard_csv():
    clear_csv_file(st.session_state)


def save_prediction(case, result, source):
    st.session_state['last_prediction'] = result
    st.session_state['last_case'] = dict(case)
    st.session_state['last_source'] = source
    st.session_state['last_time'] = datetime.now().strftime('%H:%M · %d/%m/%Y')
    st.session_state.pop('local_explanation', None)


def render_result(result, case, allow_explain=True, context='manual'):
    probability = float(result['probability'])
    cutoff = float(result['threshold'])
    positive = bool(result['positive'])
    status = 'Trên ngưỡng nguy cơ nghiên cứu' if positive else 'Dưới ngưỡng nguy cơ nghiên cứu'
    badge_class = 'status' if positive else 'status negative'
    for warning in input_warnings(case):
        st.warning(warning)
    st.markdown(f'''<section class="result">
        <div class="eyebrow">KẾT QUẢ PHÂN TÍCH · FUSION (b)</div>
        <div class="number">{probability*100:.2f}%</div>
        <div class="{badge_class}">{status}</div>
        <div class="meter" aria-hidden="true" style="position:relative"><span style="width:{probability*100:.2f}%"></span><i style="position:absolute;left:{cutoff*100:.2f}%;top:0;bottom:0;width:2px;background:#ad5328" title="Mốc F1 OOF"></i></div>
        <div class="muted-small">Mô hình dự đoán điểm xác suất của lớp dương tính là {probability*100:.2f}%. Mốc so sánh nghiên cứu được dùng tự động là <b>{cutoff*100:.2f}%</b>. {'Kết quả đạt hoặc vượt mốc này.' if positive else 'Kết quả thấp hơn mốc này.'}</div>
        </section>''', unsafe_allow_html=True)
    st.caption(f'Vạch nâu trên thanh xác suất: ngưỡng F1 OOF = {cutoff*100:.2f}%. Mức phân loại được chọn trên TRAIN/OOF, không phải ngưỡng chẩn đoán.')
    st.markdown('<div class="caution"><b>Điều quan trọng:</b> Đây là phân loại của mô hình nghiên cứu (trên/dưới ngưỡng), không xác nhận người nhập mắc hoặc không mắc NAFLD. Nhãn nghiên cứu là CAP ≥ 302 dB/m trên NHANES 2017–March 2020 sau các tiêu chí loại trừ, trong đó có sử dụng rượu có hại và viêm gan B/C. Website không phân biệt căn nguyên bệnh gan do rượu và không thay thế khám bệnh. Xác suất chưa được xác nhận hiệu chuẩn để áp dụng trên người Việt Nam.</div>',unsafe_allow_html=True)
    with st.expander('Vì sao mô hình đưa ra kết quả này? · Tín hiệu từ 4 nhóm'):
        st.write('Bốn nhóm tạo bốn xác suất riêng. Mô hình Fusion (b) cộng chúng theo trọng số đã học từ dữ liệu OOF. Trọng số **không phải** mức độ quan trọng y khoa của nhóm.')
        scores=pd.DataFrame([{
            'Nhóm':GROUP_LABELS[g],
            'Xác suất nhóm (%)':round(result['groups'][g]*100,2),
            'Trọng số Fusion (%)':round(result['weights'][g]*100,3),
            'Phần vào xác suất cuối (điểm %)':round(result['groups'][g]*result['weights'][g]*100,3),
        } for g in groups])
        st.dataframe(scores,hide_index=True,width='stretch')
        st.caption('G3/G4 có trọng số gần 0 trong cấu hình đang dùng; điều đó không có nghĩa bệnh nền hoặc lối sống không liên quan đến bệnh.')
    if allow_explain:
        with st.expander('Xem các yếu tố ảnh hưởng đến dự đoán này (giải thích cục bộ)'):
            render_local_explanation(case, probability, context=context)
    with st.expander('Mốc phân loại là gì? Vì sao không chọn ngưỡng thủ công?'):
        st.write('Website tự động dùng mốc F1 OOF đã khóa (**33,16%**) để người dùng không cần tự lựa chọn một thông số nghiên cứu khó hiểu. Mốc này được chọn trên dự đoán OOF của tập TRAIN, nhằm cân bằng Precision và Recall trong thiết kế nghiên cứu.')
        st.write('Hai mốc 50% và Recall ≥ 0,80 OOF vẫn có trong **Nghiên cứu → So sánh mô hình → OOF và ngưỡng** để đối chiếu phương pháp. Chúng không được áp dụng tự động hay điều chỉnh sau khi xem kết quả của người dùng.')


def render_local_explanation(case, probability, context='manual'):
    st.write('Giải thích ước lượng cách **26 thông tin đã nhập** làm thay đổi dự đoán của mô hình so với một giá trị nền. Kết quả không có ý nghĩa nhân quả và không đưa ra lời khuyên điều trị.')
    key=tuple(sorted(case.items()))
    cached=st.session_state.get('local_explanation')
    if cached is not None and cached.get('key') != key:
        cached = None
        st.session_state.pop('local_explanation',None)
    if st.button('Tính đóng góp của các yếu tố',key=f'compute_explain_{context}'):
        try:
            with st.spinner('Đang ước lượng Shapley từ mẫu tham chiếu VAL đã đóng băng…'):
                explanation=explain_case(case,n_permutations=24)
            if abs(explanation['probability']-probability)>1e-10:
                raise RuntimeError('Bộ giải thích không khớp với kết quả mô hình đã khóa.')
            cached={'key':key,'result':explanation}
            st.session_state['local_explanation']=cached
        except Exception as exc:
            st.error('Không tính được giải thích cho ca này.')
            st.caption('Vui lòng kiểm tra tài nguyên giải thích đã đóng gói và thử lại.')
            return
    if cached is None:
        st.caption('Nhấn nút trên nếu muốn xem giải thích. Phần này cần tính riêng, không bắt buộc để nhận dự đoán.')
        return
    explanation=cached['result']
    st.caption(f"Giá trị nền {100*explanation['baseline']:.2f}% + tổng đóng góp {100*(probability-explanation['baseline']):+.2f} điểm % = {100*probability:.2f}%.")
    lookup=input_feature_groups(preprocessor)
    group_per_var={name:next((g for g,features in groups.items() if lookup[name][0] in features),'—') for name in lookup}
    frame=pd.DataFrame([{
        'Biến':LABELS.get(field,(field,''))[0], 'Nhóm':group_per_var[field],
        'Đóng góp (điểm %)':float(impact)*100,
    } for field,impact in explanation['contributions'].items()])
    frame['Độ lớn']=frame['Đóng góp (điểm %)'].abs()
    frame=frame.sort_values('Độ lớn',ascending=False)
    top=frame.head(10).sort_values('Đóng góp (điểm %)')
    fig=go.Figure(go.Bar(x=top['Đóng góp (điểm %)'],y=top['Biến'],orientation='h',
          marker_color=[COLOR_PRIMARY if x>=0 else COLOR_SECONDARY for x in top['Đóng góp (điểm %)']],
          hovertemplate='%{y}<br>%{x:+.3f} điểm %<extra></extra>'))
    fig.add_vline(x=0,line_color='#849493',line_width=1)
    fig.update_layout(height=425,margin=dict(l=5,r=10,t=10,b=40),
        paper_bgcolor='white',plot_bgcolor='white',font=dict(color='#1b3137'),
        xaxis_title='Thay đổi xác suất so với nền (điểm phần trăm)',yaxis_title='')
    st.plotly_chart(fig,width='stretch',key=f'local_shap_chart_{context}')
    st.caption('Xanh rêu: làm tăng dự đoán. Nâu đất: làm giảm dự đoán. Độ dài thanh là đóng góp của mô hình, không phải nguyên nhân gây bệnh.')
    group_scores=frame.groupby('Nhóm',as_index=False)['Đóng góp (điểm %)'].sum()
    with st.expander('Đóng góp tổng theo nhóm và đủ 26 biến'):
        st.dataframe(group_scores,hide_index=True,width='stretch')
        st.dataframe(frame.drop(columns='Độ lớn'),hide_index=True,width='stretch')
        st.caption('Phép giải thích xấp xỉ sử dụng 12 mẫu tham chiếu VAL và 24 hoán vị. Không đồng nhất với SHAP toàn cục tuần 9.')


def input_field(code):
    label, unit = LABELS.get(code,(code,''))
    label = FIELD_NAMES.get(code,label)
    if code in ('RIDAGEYR','RIAGENDR','RIDRETH3'):
        label += ' *'
    if code in NUMERIC_CODES:
        display = f'{label} ({unit})' if unit and unit != 'nan' else label
        unit_help = 'Đơn vị: '+unit+'. ' if unit and unit!='nan' else ''
        st.text_input(display,key='field_'+code,on_change=remember_field,args=(code,),placeholder='Nhập số' if code=='RIDAGEYR' else 'Để trống nếu chưa có dữ liệu',
                      help=unit_help+NUMERIC_HELP.get(code,''))
    else:
        st.radio(label,options=[None]+list(CHOICES[code]) if code in OPTIONAL_CATEGORIES else list(CHOICES[code]),
                 format_func=lambda value: 'Không rõ (điền thiếu từ TRAIN)' if value is None else CHOICES[code][value],
                 index=0 if code in OPTIONAL_CATEGORIES else None,key='field_'+code,
                 on_change=remember_field,args=(code,),help=CATEGORY_HELP.get(code,''),horizontal=len(CHOICES[code])<=4)


def manual_form():
    # Restoring persistent values *before* declaring widgets is essential:
    # Streamlit deletes invisible widget keys when user navigates to other pages.
    restore_draft(st.session_state, NUMERIC_CODES, CATEGORY_CODES)
    if st.session_state.get('form_error'):
        st.error('Vui lòng kiểm tra dữ liệu: '+st.session_state['form_error'])
    st.markdown('<div class="notice">Điền <b>3 trường có dấu *</b> (tuổi, giới tính, nhóm dân tộc NHANES). Bệnh nền/lối sống có thể chọn <b>Không rõ</b>; số đo chưa có để trống. Không nhập 0 để thay thế giá trị thiếu. Dấu phẩy hoặc chấm dùng làm dấu thập phân, không dùng phân cách hàng nghìn.</div>',unsafe_allow_html=True)
    a,b=st.columns(2,gap='small')
    with a:
        st.button('Thử ca A · trên ngưỡng',on_click=load_demo,args=(EXAMPLE_A,),width='stretch')
    with b:
        st.button('Thử ca B · dưới ngưỡng',on_click=load_demo,args=(EXAMPLE_B,),width='stretch')
    st.caption('Hai ca ví dụ là dữ liệu giả lập, không phải hồ sơ người bệnh. Các xét nghiệm glucose, triglyceride, HDL và cholesterol yêu cầu mg/dL, không phải mmol/L.')
    st.caption('Bốn nhóm là các nguồn thông tin nghiên cứu; cấu hình Fusion (b) seed 42 gán trọng số gần 0 cho G3/G4, nhưng điều đó không phủ nhận ý nghĩa lâm sàng của chúng.')
    with st.container(border=True):
        for index, (group,codes) in enumerate(GROUP_CODES.items()):
            with st.expander(f'{index+1:02d}. {GROUP_LABELS[group]} · {len(codes)} thông tin',expanded=(index==0 or group in st.session_state.get('error_groups',[]))):
                st.caption(GROUP_DESCRIPTIONS[group])
                left,right=st.columns(2)
                for i,code in enumerate(codes):
                    with (left if i%2==0 else right):
                        input_field(code)
        present = sum(bool(str(st.session_state.get('field_'+code,'')).strip()) for code in NUMERIC_CODES)
        st.caption(f'Đã điền {present}/19 số đo; các số đo còn thiếu sẽ được điền theo quy tắc TRAIN.')
        if not any(str(st.session_state.get('field_'+c,'')).strip() for c in ('BMXBMI','BMXWAIST','BMXHIP')):
            st.warning('Chưa nhập BMI, vòng eo và vòng mông: ba tín hiệu nhân trắc quan trọng. Nên có ít nhất một trong ba trước khi dự đoán.')
        draft_case = None
        try:
            draft_case = validate_case({code: st.session_state.get('field_'+code) for code in ALL_CODES})
        except InputError:
            pass
        core_outliers = core_measurement_extrapolations(draft_case) if draft_case is not None else []
        if core_outliers:
            detail = '; '.join(f"{FIELD_NAMES[code]} {value:g} (TRAIN: {low:g}–{high:g})" for code,value,low,high in core_outliers)
            st.warning('Một hoặc nhiều số đo nhân trắc nằm ngoài khoảng quan sát trong TRAIN: '+detail+'. Mô hình phải ngoại suy ở các biến này.')
            st.checkbox('Tôi đã kiểm tra các số đo ngoài khoảng TRAIN và vẫn muốn tiếp tục', key='confirm_core_extrapolation')
        st.caption('Khi dự đoán, hệ thống tự sử dụng ngưỡng F1 OOF đã xác lập trong nghiên cứu.')
        action,discard,reset=st.columns([2.2,1.1,1.1],gap='small')
        with action:
            pressed=st.button('Xem kết quả dự đoán',type='primary',width='stretch',
                              key='predict_manual',icon=':material/monitor_heart:')
        with discard:
            st.button('Xóa kết quả',width='stretch',on_click=clear_last_result,
                      key='clear_manual_result',icon=':material/delete_outline:')
        with reset:
            st.button('Nhập ca mới',width='stretch',on_click=start_new_case,
                      key='new_manual_case',icon=':material/restart_alt:')
    if pressed:
        keep_draft(st.session_state,ALL_CODES)
        raw={code:st.session_state.get('field_'+code) for code in ALL_CODES}
        try:
            case=validate_case(raw)
            if core_measurement_extrapolations(case) and not st.session_state.get('confirm_core_extrapolation', False):
                st.session_state['form_error']='Có số đo BMI, vòng eo hoặc vòng mông nằm ngoài khoảng quan sát trong TRAIN. Hãy xác nhận đã kiểm tra trước khi tiếp tục.'
                st.rerun()
            result=predict_case(case,DEFAULT_MODE)
        except InputError as exc:
            st.session_state['form_error']=str(exc)
            st.session_state['error_groups']=[group for group,codes in GROUP_CODES.items()
                if any(FIELD_NAMES.get(code,code) in str(exc) for code in codes)]
            st.rerun()
        except Exception as exc:
            st.error('Không thể chạy mô hình với thông tin này. Vui lòng kiểm tra dữ liệu.')
            st.caption('Chi tiết lỗi đã được ghi tại terminal chạy Streamlit.')
        else:
            st.session_state.pop('form_error',None)
            st.session_state.pop('error_groups',None)
            save_prediction(case,result,'Nhập trực tiếp')
    if st.session_state.get('last_prediction') is not None and st.session_state.get('last_source')=='Nhập trực tiếp':
        current_raw={code:st.session_state.get('field_'+code) for code in ALL_CODES}
        try:
            unchanged=validate_case(current_raw)==st.session_state.get('last_case')
        except InputError:
            unchanged=False
        if unchanged:
            st.markdown('### Kết quả gần nhất')
            st.caption('Đã giữ trong phiên · '+st.session_state.get('last_time',''))
            render_result(st.session_state['last_prediction'],st.session_state['last_case'],context='manual')
            result_clear,result_new=st.columns(2,gap='small')
            with result_clear:
                st.button('Xóa kết quả này',on_click=clear_last_result,
                          key='clear_result_below',width='stretch',icon=':material/delete_outline:')
            with result_new:
                st.button('Nhập thông tin ca mới',on_click=start_new_case,
                          key='start_new_below',width='stretch',icon=':material/restart_alt:')
        else:
            st.warning('Thông tin đang chỉnh đã khác lần dự đoán trước. Kết quả cũ vẫn được giữ tại trang Giải thích, nhưng không áp dụng cho thông tin mới. Hãy bấm “Xem kết quả dự đoán” để cập nhật.')


def csv_form():
    st.markdown('<div class="notice"><b>Nhập nhiều ca từ CSV:</b> tải tệp mẫu gồm 26 cột có mã NHANES, điền số đo hoặc để trống những phép đo chưa có. Có thể dùng tối đa 100 dòng mỗi lần. Website không lưu tệp lên cơ sở dữ liệu và không bổ sung dữ liệu này vào các biểu đồ nghiên cứu.</div>',unsafe_allow_html=True)
    st.download_button('Tải CSV mẫu · 2 ca giả lập',data=csv_template(),file_name='NAFLD_Insight_mau_26_bien.csv',
                       mime='text/csv',width='content')
    with st.expander('Xem hướng dẫn 26 cột CSV và mã lựa chọn'):
        st.dataframe(pd.DataFrame(csv_columns_guide(LABELS)),hide_index=True,width='stretch')
        st.caption('Ví dụ: giới tính RIAGENDR: 1 = Nam, 2 = Nữ. Không thay đổi tên cột dù dùng Excel.')
    upload_key='csv_upload_'+str(st.session_state.get('csv_upload_epoch',0))
    file=st.file_uploader('Chọn tệp CSV UTF-8',type=['csv'],key=upload_key,
                          on_change=remember_csv_widget,args=(upload_key,),
                          help='Tối đa 1 MB và 100 dòng. Hỗ trợ dấu phân cách phẩy hoặc chấm phẩy.')
    if file is not None:
        # Also handle an upload on the initial render on older Streamlit versions.
        keep_csv_file(st.session_state,file.getvalue(),file.name)
    payload=st.session_state.get('csv_payload')
    if payload is None:
        st.info('Chưa chọn tệp. Bạn có thể tải mẫu phía trên, điền thông tin và tải lên tại đây.')
        return
    row_name,col_discard=st.columns([3,1],vertical_alignment='center')
    with row_name:
        st.caption('Tệp trong phiên: '+st.session_state.get('csv_filename','CSV đã chọn')+' · Chuyển trang vẫn giữ dữ liệu và kết quả.')
    with col_discard:
        st.button('Bỏ tệp CSV',on_click=discard_csv,width='stretch', key='clear_csv_file')
    signature=st.session_state['csv_signature']
    try:
        parsed=parse_csv_bytes(payload)
    except InputError as exc:
        st.error(str(exc));return
    st.caption(f'Đã đọc {len(parsed.rows)} dòng dữ liệu · {len(parsed.errors)} dòng cần sửa. Dòng CSV được đếm theo số dòng thực tế, kể cả dòng trống.')
    valid_rows = [(i,case) for i,case in zip(parsed.row_numbers,parsed.rows) if i not in parsed.errors]
    incomplete = sum(bool(input_warnings(case)) for i,case in valid_rows)
    extrapolated_rows = [(i, core_measurement_extrapolations(case)) for i,case in valid_rows]
    extrapolated_rows = [(i, flags) for i,flags in extrapolated_rows if flags]
    if incomplete:
        st.warning(f'{incomplete} dòng có cảnh báo về phạm vi TRAIN, đơn vị hoặc dữ liệu thiếu; hãy xem chi tiết trước khi sử dụng kết quả.')
    confirm_csv_extrapolation = True
    if extrapolated_rows:
        row_details = '; '.join(f"dòng {row}: {', '.join(FIELD_NAMES[code] for code,_,_,_ in flags)}" for row,flags in extrapolated_rows)
        st.warning('Các số đo BMI/vòng eo/vòng mông ở ngoài khoảng quan sát trong TRAIN tại '+row_details+'. Mô hình phải ngoại suy ở những biến này.')
        confirm_csv_extrapolation = st.checkbox('Tôi đã kiểm tra các dòng có số đo ngoài khoảng TRAIN và vẫn muốn tiếp tục', key='confirm_csv_core_extrapolation')
    if parsed.extra_columns:
        st.warning('Các cột bổ sung không sử dụng: '+', '.join(parsed.extra_columns))
    if parsed.errors:
        st.warning('Một số dòng chưa hợp lệ. Các dòng này sẽ không được suy luận.')
        with st.expander('Xem lỗi theo dòng',expanded=True):
            st.dataframe(pd.DataFrame([{'Dòng CSV':i,'Lý do':message} for i,message in parsed.errors.items()]),hide_index=True)
    st.markdown('#### Xem trước dữ liệu (không hiển thị toàn bộ khi có nhiều dòng)')
    preview=[]
    for i,case in zip(parsed.row_numbers[:6],parsed.rows[:6]):
        preview.append({'Dòng CSV':i,'Tuổi':case.get('RIDAGEYR'),'BMI':case.get('BMXBMI'),
                        'Vòng eo':case.get('BMXWAIST'), 'Trạng thái':'Cần sửa' if i in parsed.errors else 'Hợp lệ'})
    st.dataframe(pd.DataFrame(preview),hide_index=True,width='stretch')
    if st.button('Dự đoán những dòng hợp lệ',type='primary',width='stretch',disabled=bool(extrapolated_rows and not confirm_csv_extrapolation)):
        with st.spinner('Đang phân tích bằng Fusion (b) đã khóa…'):
            records,cases=batch_predict(parsed,predict_case)
        st.session_state['batch_signature']=signature
        st.session_state['batch_results']=records
        st.session_state['batch_cases']=cases
    if signature != st.session_state.get('batch_signature'):
        if str(st.session_state.get('last_source','')).startswith('CSV – xem từng dòng'):
            for item in ('last_prediction','last_case','local_explanation'):
                st.session_state.pop(item,None)
        st.info('Nhấn nút dự đoán để xem kết quả của tệp CSV hiện tại.')
        return
    records=st.session_state.get('batch_results')
    if records is None:
        return
    st.markdown('### Kết quả theo từng dòng')
    st.dataframe(pd.DataFrame(records),width='stretch',hide_index=True)
    st.caption('Trên/dưới ngưỡng là nhãn dự đoán theo mô hình nghiên cứu, không phải kết quả xét nghiệm hay chẩn đoán. Bảng xuất chỉ gồm kết quả, ngưỡng và phiên bản mô hình, không chứa dữ liệu đầu vào.')
    data=pd.DataFrame(records).to_csv(index=False).encode('utf-8-sig')
    st.download_button('Xuất bảng kết quả CSV',data=data,file_name='NAFLD_Insight_ket_qua_du_doan.csv',mime='text/csv')
    cases=st.session_state.get('batch_cases',{})
    if cases:
        chosen=st.selectbox('Xem chi tiết một dòng đã dự đoán',options=list(cases),format_func=lambda i:f'Dòng {i}',key='inspect_row')
        if st.button('Hiển thị giải thích cho dòng này', key='csv_choose_row'):
            case,result=cases[chosen]
            save_prediction(case,result,f'CSV – xem từng dòng {chosen}')
            st.rerun()
        if st.session_state.get('last_prediction') is not None and str(st.session_state.get('last_source','')).startswith('CSV – xem từng dòng'):
            st.caption('Chi tiết nguồn: '+st.session_state.get('last_source',''))
            render_result(st.session_state['last_prediction'],st.session_state['last_case'],context='csv')


def show_research_image(filename, caption):
    path=ROOT/'resource/figures'/filename
    if not path.is_file():
        st.warning('Chưa có hình minh chứng: '+filename+' (khôi phục resource/figures).')
        return
    st.image(str(path),caption=caption,width='stretch')


def show_research_overview():
    columns_stats([('6.688','Quan sát trong cohort'),('4.680','TRAIN'),('1.004','VAL'),('1.004','TEST')])
    research_image=brand_image_bytes('research')
    if research_image is not None:
        rcol1,rcol2=st.columns([2.2,1],vertical_alignment='center')
        with rcol1:
            st.markdown('### Lộ trình thực nghiệm')
            st.write('Năm giai đoạn có bảng số liệu lưu, từ baseline đến kiểm chứng đóng góp bằng SHAP. Tất cả được đọc từ nguồn nghiên cứu đã khóa.')
        with rcol2:st.image(research_image,width='stretch')
    else:
        st.markdown('### Lộ trình thực nghiệm')
    steps=[('Tuần 5','So sánh 4 thuật toán nền trên VAL.'),
           ('Tuần 6','Kiểm định chéo và tinh chỉnh trên TRAIN.'),
           ('Tuần 7','Bốn nhóm đặc trưng, OOF, Fusion và Stacking.'),
           ('Tuần 8','Ablation: lần lượt loại từng nhóm để đánh giá ảnh hưởng.'),
           ('Tuần 9','SHAP toàn cục trên VAL, giải thích cấp biến và cấp nhóm.')]
    for col,(title,summary) in zip(st.columns(5,gap='small'),steps):
        with col:
            st.markdown(f'<div class="instruction-box"><div class="site-overline">{title}</div><p>{summary}</p></div>',unsafe_allow_html=True)
    st.markdown('<div class="caution">Các số liệu là kết quả thực nghiệm đã lưu. Ứng dụng không tái huấn luyện hay tính lại trên TEST: các bảng TEST được đọc từ kết quả tổng hợp có sẵn (tuần 8–9); không đưa dữ liệu người dùng vào tập nghiên cứu.</div>',unsafe_allow_html=True)
    st.markdown('### Kết quả tổng hợp trên VAL (trung bình 5 seed)')
    df=load_evidence('comparison_val')
    unique=df.drop_duplicates(subset=['Mô hình']).copy()
    fig=go.Figure(go.Bar(x=unique['Mô hình'],y=unique['AUPRC'].map(val_metric_number),marker_color=COLOR_PRIMARY,
        text=unique['AUPRC'].map(lambda v:f'{val_metric_number(v):.4f}'),textposition='outside'))
    fig.update_layout(height=340,margin=dict(l=5,r=5,t=18,b=70),yaxis=dict(range=[0,.8],title='AUPRC trên VAL'),
        paper_bgcolor='#fff',plot_bgcolor='#fff',font=dict(color='#1b3137'),xaxis_title='')
    st.plotly_chart(fig,width='stretch')
    mark_source('comparison_val')
    st.info('AUPRC trên VAL không phải bằng chứng Fusion (b) thắng trên TEST. Trên TEST: Fusion (b) = 0,6881 và LightGBM gộp = 0,6910 (trung bình 5 seed). Chưa đủ bằng chứng thống kê khẳng định Fusion (b) vượt LightGBM gộp. Xem bảng TEST trong mục So sánh mô hình.')


def show_research_models():
    tabs=st.tabs(['Baseline tuần 5','5-fold CV & tuning','Fusion / Stacking tuần 7','OOF và ngưỡng','Đối chiếu VAL–TEST đã lưu'])
    with tabs[0]:
        st.markdown('#### Bốn mô hình nền')
        st.write('Bốn thuật toán được thử trước khi thu hẹp còn Logistic Regression và LightGBM làm ứng viên mô hình nhóm. Bảng này là **VAL tuần 5**, không phải bốn kết quả dự đoán của cùng một ca người dùng.')
        frame=baseline_val_models()
        cols=['mo_hinh','accuracy','precision','recall','f1','auroc','auprc']
        st.dataframe(frame[cols].rename(columns=dict(mo_hinh='Mô hình',accuracy='Accuracy',precision='Precision',
          recall='Recall',f1='F1',auroc='AUROC',auprc='AUPRC')),hide_index=True,width='stretch')
        st.bar_chart(frame.set_index('mo_hinh')[['auroc','auprc']],color=[COLOR_PRIMARY,COLOR_SECONDARY],stack=False)
        mark_source('baseline')
    with tabs[1]:
        st.markdown('#### Kiểm định chéo trên TRAIN')
        st.write('Stratified 5-fold: mỗi quan sát được dự đoán khi nó nằm ở phần dữ liệu không dùng để huấn luyện mô hình tương ứng. Mean ± SD thể hiện trung bình và độ lệch chuẩn qua các fold.')
        st.dataframe(load_evidence('cv'),width='stretch',hide_index=True)
        mark_source('cv')
        st.markdown('#### Kết quả trước và sau tinh chỉnh')
        st.dataframe(load_evidence('tuning'),width='stretch',hide_index=True)
        mark_source('tuning')
    with tabs[2]:
        st.markdown('#### So sánh các phương pháp kết hợp')
        st.write('Fusion (a): trung bình xác suất; Fusion (b): trọng số học trên OOF; Stacking: mô hình tầng hai học từ các dự đoán OOF.')
        df=load_evidence('comparison_val')
        st.dataframe(df[['Mô hình','Ngưỡng','Accuracy','Precision','Recall','F1','AUROC','AUPRC']],hide_index=True,width='stretch')
        mark_source('comparison_val')
        st.caption('Không kết luận Fusion (b) tốt hơn Stacking về mọi chỉ số: AUPRC trung bình của Stacking nhỉnh hơn khoảng 0,0011.')
    with tabs[3]:
        st.markdown('#### OOF là gì?')
        st.write('OOF (Out-of-Fold) tạo xác suất trên các phần TRAIN không dùng để huấn luyện mô hình tại lượt đó. Các xác suất này được dùng để học trọng số và chọn ngưỡng mà không tối ưu trực tiếp trên VAL.')
        st.dataframe(load_evidence('oof'),hide_index=True,width='stretch')
        mark_source('oof')
        st.markdown('#### Ba ngưỡng trong nghiên cứu')
        frame=pd.DataFrame([('F1 OOF — mặc định cho người dùng',thresholds['threshold_f1_oof'],
                             'Lựa chọn nhằm tối ưu F1 trên TRAIN OOF.'),
                             ('Mốc đối chiếu cố định',thresholds['threshold_0_5'],
                             'Ngưỡng 50% dùng làm tham chiếu.'),
                             ('Recall ≥ 0,80 trên OOF',thresholds['threshold_recall80_oof'],
                             'Ưu tiên Recall trên TRAIN OOF, không bảo đảm 80% ngoài mẫu.')],
                             columns=['Ngưỡng','Giá trị','Ý nghĩa'])
        frame['Giá trị']=frame['Giá trị'].map(lambda n:round(100*n,2))
        st.dataframe(frame.rename(columns={'Giá trị':'Mốc (%)'}),hide_index=True,width='stretch')
        st.write('Ngưỡng không thay đổi xác suất mô hình. Nó chỉ quyết định kết quả trên/dưới mốc thống kê. Người dùng không cần phải tự chọn ngưỡng.')


    with tabs[4]:
        st.markdown('#### Đối chiếu AUPRC VALIDATION và TEST · kết quả đã lưu')
        st.caption('Các giá trị TEST dưới đây là số liệu tổng hợp đã khóa tuần 8–9. Không nạp dữ liệu TEST, không tính lại dự đoán và không dùng TEST để chọn lại model.')
        df = load_stored_test_summary()
        st.dataframe(df, hide_index=True, width='stretch')
        show_research_image('hinh_val_vs_test.png','Hình VAL–TEST tổng hợp tuần 9 (bản lưu nghiên cứu)')
        st.markdown('**Kết luận:** Fusion (b) được giữ làm mô hình minh họa vì tính diễn giải theo nhóm, không phải vì thắng mọi mô hình trên TEST. Trung bình 5 seed, AUPRC TEST Fusion (b) 0,6881 thấp hơn LightGBM gộp 0,6910. Kiểm định bootstrap ghép cặp trong nghiên cứu không đủ bằng chứng để khẳng định Fusion (b) tốt hơn LightGBM gộp.')
        st.caption('Nguồn: KetQua_Tuan9/bang/val_vs_test.csv; KetQua_Tuan9/bang/danh_gia_gop_val_test.csv. Đây là kết quả sau khi TEST đã được mở theo nhật ký tuần 8, không dùng để điều chỉnh mô hình.')


def show_research_contribution():
    a,b,c=st.tabs(['Bốn nhóm và trọng số','Ablation tuần 8','SHAP toàn cục tuần 9'])
    with a:
        st.write('Mỗi nhóm được thử độc lập, sau đó được kết hợp bằng trọng số. Đóng góp dự đoán **không đồng nhất** với tầm quan trọng y khoa.')
        st.dataframe(load_evidence('group_val'),hide_index=True,width='stretch')
        mark_source('group_val')
        st.markdown('#### Trọng số Fusion (b) seed 42')
        st.dataframe(pd.DataFrame({'Nhóm':[GROUP_LABELS[g] for g in groups],
            'Trọng số (%)':[round(weights[g]*100,3) for g in groups]}),hide_index=True)
        st.caption('G3 và G4 có trọng số gần bằng 0: đây là kết quả tối ưu trên OOF, không phủ nhận vai trò y học của chúng.')
        show_research_image('Hinh_KienTruc_Fusion.png','Kiến trúc G1–G4 và Fusion (b) theo nghiên cứu tuần 7–9')
    with b:
        st.markdown('#### Khi bỏ từng nhóm, AUPRC trên VAL thay đổi ra sao?')
        df=group_ablation_val_means()
        st.dataframe(df.rename(columns={'cau_hinh':'Cấu hình','AUPRC_val_mean':'AUPRC VAL trung bình',
             'AUPRC_val_sd':'SD', 'AUROC_val_mean':'AUROC VAL trung bình','n_seed':'Số seed'}),hide_index=True,width='stretch')
        st.bar_chart(df.set_index('cau_hinh')[['AUPRC_val_mean']],color=COLOR_PRIMARY)
        mark_source('ablation_val')
        st.caption('Theo phương pháp tuần 8, trọng số được tối ưu lại khi loại nhóm; không giữ nguyên trọng số khi loại cột.')
        show_research_image('hinh_ablation.png','Ablation trên TEST theo hồ sơ tuần 8; hình đã lưu, không tính lại')
    with c:
        st.markdown('#### Mức đóng góp trung bình của đặc trưng trên VAL')
        show_research_image('hinh_shap_bar_fusion_b.png','Global SHAP Fusion (b), tuần 9, tập VAL')
        show_research_image('hinh_shap_nhom.png','Độ lớn SHAP theo nhóm G1–G4 trên VAL')
        with st.expander('Xem thêm SHAP beeswarm và hai ca giải thích minh họa'):
            show_research_image('hinh_shap_beeswarm_fusion_b.png','SHAP beeswarm Fusion (b) trên VAL')
            show_research_image('hinh_shap_waterfall_TP.png','SHAP waterfall, ví dụ đúng dương trên VAL')
            show_research_image('hinh_shap_waterfall_FN.png','SHAP waterfall, ví dụ bỏ sót trên VAL')
        top=load_evidence('shap_global')
        top=top.loc[top['phan']=='top15_fusion_b']
        st.dataframe(top[['muc','nhom','gia_tri','ty_trong_pct']].rename(columns={
            'muc':'Đặc trưng','nhom':'Nhóm','gia_tri':'Mean |SHAP| (điểm %)','ty_trong_pct':'Tỷ trọng (%)'}),
            hide_index=True,width='stretch')
        mark_source('shap_global')
        st.info('SHAP phản ánh cách mô hình sử dụng dữ liệu. Không suy luận quan hệ nhân quả, mức độ bệnh hoặc lợi ích điều trị từ một thanh SHAP.')


def research_sources():
    st.markdown('### Nguồn gốc bảng số liệu')
    for name,description in SOURCE_DESCRIPTIONS.items():
        st.markdown(f'- **{name}**: {description}')
    st.markdown('### Giải nghĩa các tập dữ liệu')
    st.markdown('**TRAIN:** dữ liệu dùng để học mô hình. **CV:** đánh giá qua các fold của TRAIN. **OOF:** xác suất dự đoán ngoài fold trên TRAIN. **VAL:** tập xác thực. **TEST:** tập đánh giá cuối đã mở trong tuần 8; website chỉ hiển thị bảng tổng hợp TEST đã lưu, không nạp hay dự đoán lại trên TEST.')
    st.markdown('### Trạng thái kiểm định')
    st.write('Manifest SHA-256 kiểm tra 5 mô hình/bộ tiền xử lý, ba JSON cấu hình và 12 mẫu VAL tham chiếu trước khi sử dụng; thay đổi trái phép tệp được khóa sẽ khiến app từ chối suy luận. Nhập CSV chỉ dự đoán, không trộn dữ liệu vào TRAIN, OOF, VAL hay TEST.')
    st.write('Ứng dụng không lưu hồ sơ người dùng xuống ổ đĩa hay cơ sở dữ liệu. Thông tin đang điền, kết quả dự đoán gần nhất và kết quả CSV được giữ trong session Streamlit khi chuyển trang. Người dùng có thể xóa kết quả hoặc nhập ca mới; tải lại phiên từ đầu hoặc đóng phiên có thể làm mất dữ liệu.')
    st.caption('Giới hạn nghiên cứu: không có kiểm định ngoài trên quần thể Việt Nam; kết quả TRAIN/VAL/TEST là nghiên cứu nội bộ, một số phân tích TEST là khám phá sau khi mở TEST; không thể dùng để chứng minh quan hệ nhân quả.')
    st.caption('Hiệu chuẩn trên TEST đã được đo: Fusion (b) có độ dốc khoảng 1,40 và hệ số chặn khoảng +0,27. Chưa đủ cơ sở để xem điểm dự đoán là xác suất bệnh cá nhân đã hiệu chuẩn.')
    st.caption('Kiểm thử chức năng Python không thay cho nghiệm thu đầy đủ 15 luồng giao diện và đánh giá lâm sàng độc lập.')


site_header()
page = st.session_state.get('page','Giới thiệu')

if page=='Giới thiệu':
    cover = brand_image_bytes('cover')
    hero_left,hero_right=st.columns([1.7,1],vertical_alignment='top',gap='medium')
    with hero_left:
        st.markdown('<section class="hero-panel"><div class="hero-tag">KHÓA LUẬN CỬ NHÂN · HUIT</div><div class="hero-title">Dự đoán nguy cơ gan nhiễm mỡ không do rượu (NAFLD) từ dữ liệu lâm sàng đa nhóm bằng mô hình học máy</div><div class="hero-desc">Điền thông tin sức khỏe hoặc tải CSV để xem mô hình phân loại và những yếu tố được sử dụng. Kết quả chỉ phục vụ minh họa nghiên cứu.</div></section>',unsafe_allow_html=True)
    with hero_right:
        if cover is not None:
            st.markdown('<div class="hero-aside hero-with-image"><img src="'+image_to_data_uri(cover)+'" alt="Ảnh minh họa cố định của NAFLD Insight"/></div>',unsafe_allow_html=True)
        else:
            st.markdown('<section class="hero-aside"><div class="site-overline">CÔNG CỤ MINH BẠCH</div><h3>Không chỉ có một con số</h3><p>Kết quả gồm xác suất mô hình, phân loại theo ngưỡng đã khóa và phần giải thích dễ hiểu.</p><p><b>Không chẩn đoán bệnh.</b> Không lưu hồ sơ vào tập nghiên cứu. Có số liệu đối chiếu từ tuần 5–9.</p></section>',unsafe_allow_html=True)
    st.button('Bắt đầu dự đoán',type='primary',on_click=take_to_prediction,icon=':material/arrow_forward:')
    columns_stats([('26','Thông tin đầu vào'),('04','Nhóm thông tin'),('01','Kết quả dự đoán'),('03','Bước sử dụng')])
    st.markdown('### Ba bước sử dụng')
    for column,index,title,desc in zip(st.columns(3),('01','02','03'),
        ('Nhập thông tin','Xem kết quả','Hiểu lý do'),
        ('Điền trực tiếp hoặc nhập CSV theo mẫu. Các ô số đo chưa có có thể bỏ trống.',
         'Nhấn một nút duy nhất. Hệ thống tự dùng ngưỡng nghiên cứu đã khóa.',
         'Xem tín hiệu G1–G4 và, khi muốn, giải thích các đặc trưng theo ca.')):
        with column: step_card(index,title,desc)
    st.markdown('### Bốn nhóm dữ liệu được sử dụng')
    for col, (name,title) in zip(st.columns(4,gap='small'), GROUP_LABELS.items()):
        with col:
            st.markdown(f'<div class="group-card"><div class="site-overline">{name}</div><strong>{title}</strong><p>{GROUP_DESCRIPTIONS[name]}</p></div>',unsafe_allow_html=True)
    st.markdown('<div class="caution"><b>Phạm vi sử dụng:</b> Cohort NHANES 2017–03/2020 (6.688 người, 1.830 nhãn dương tính); nhãn nghiên cứu được xác định theo CAP ≥ 302 dB/m, loại trừ sử dụng rượu có hại và viêm gan B/C theo giao thức. Mô hình không xác định căn nguyên bệnh, không được kiểm định trên dân số Việt Nam và không thay thế chẩn đoán y khoa.</div>',unsafe_allow_html=True)
    with st.expander('Tại sao nghiên cứu sử dụng bốn thuật toán nền?'):
        st.write('Logistic Regression, Random Forest, XGBoost và LightGBM được dùng để đối chứng ở tuần 5. Từ tuần 6–7, nhóm chọn Logistic Regression và LightGBM làm ứng viên cho các nhóm G1–G4. Phần Nghiên cứu cho phép kiểm tra đầy đủ các bảng kết quả.')

elif page=='Dự đoán':
    heading('DỰ ĐOÁN · CÓ GIẢI THÍCH','Nhập dữ liệu và xem kết quả',
            'Chọn cách nhập thuận tiện cho bạn. Hệ thống dùng một ngưỡng mặc định đã được xác định từ kết quả nghiên cứu; không cần tự chọn các thuật toán hoặc ngưỡng.')
    main,guide=st.columns([3.5,1.25],gap='large')
    with main:
        manual,csv_tab=st.tabs(['Nhập thông tin trực tiếp','Nhập từ tệp CSV'])
        with manual:manual_form()
        with csv_tab:csv_form()
    with guide:
        st.markdown('### Hướng dẫn nhanh')
        st.markdown('<div class="instruction-box"><div class="site-overline">01 / CHUẨN BỊ</div><strong>Số đo thực tế</strong><p>Chuẩn bị tuổi, vòng eo, BMI và kết quả xét nghiệm nếu có.</p></div>',unsafe_allow_html=True)
        st.markdown('<div class="instruction-box"><div class="site-overline">02 / GIÁ TRỊ THIẾU</div><strong>Không đo ≠ 0</strong><p>Có thể để trống số chưa đo; chọn “Không rõ” cho bệnh nền/lối sống. Cảnh báo khi quá ít thông tin.</p></div>',unsafe_allow_html=True)
        st.markdown('<div class="instruction-box"><div class="site-overline">03 / KẾT LUẬN</div><strong>Một ngưỡng duy nhất</strong><p>Hệ thống tự dùng mốc F1 OOF được khóa. Không cần tự chọn.</p></div>',unsafe_allow_html=True)
        st.caption('Dữ liệu nhập không được thêm vào dữ liệu nghiên cứu.')

elif page=='Giải thích':
    heading('ĐỌC KẾT QUẢ','Xác suất và các yếu tố có ý nghĩa gì?',
            'Trang này giải nghĩa những con số mà bạn nhìn thấy. Không cần tìm hiểu công thức toán học để sử dụng tính năng dự đoán.')
    with st.expander('Xác suất 59,49% có nghĩa tôi bị bệnh 59,49%?',expanded=True):
        st.write('Không. Đây là điểm dự đoán lớp CAP ≥ 302 dB/m theo nghiên cứu. Nhóm đã khảo sát hiệu chuẩn trên TEST (độ dốc ~1,40, hệ số chặn ~+0,27), nhưng chưa có kiểm định ngoài hay hiệu chuẩn đủ cho người Việt. Trên ngưỡng chỉ là phân loại của mô hình, không phải chẩn đoán.')
    with st.expander('Nhãn phân loại của mô hình khác gì chẩn đoán lâm sàng?'):
        st.write('Nhãn dự đoán được tạo bằng cách so điểm dự đoán với ngưỡng F1 OOF 33,16%. Chẩn đoán bệnh cần đánh giá y tế, căn nguyên và tiêu chí lâm sàng. Trên TEST seed 42, PPV khoảng 58,17% và NPV khoảng 89,01% tại ngưỡng này; các tỷ lệ không bảo đảm trên quần thể khác. Dưới ngưỡng không loại trừ bệnh.')
    with st.expander('AST, ALT, GGT, HbA1c là gì?'):
        st.write('AST, ALT, GGT là các enzyme xét nghiệm máu thường liên quan đến đánh giá gan hoặc gan mật. HbA1c phản ánh đường huyết trong vài tháng gần đây. Không có chỉ số nào trong số này tự xác nhận NAFLD.')
    with st.expander('Tại sao một số ô số liệu có thể bỏ trống?'):
        st.write('Bộ tiền xử lý có cơ chế xử lý thông tin thiếu đã được học từ TRAIN. Nếu chưa đo, để trống; không nhập 0 như thể đó là giá trị thật. Dự đoán khi thiếu nhiều thông tin có thể kém đáng tin cậy hơn.')
    with st.expander('Trọng số Fusion có phải mức độ ảnh hưởng lên sức khỏe?'):
        st.write('Không. Trọng số xác định cách cộng xác suất của bốn mô hình nhóm. SHAP là một cách giải thích khác, xem biến nào làm tăng hoặc giảm điểm dự đoán tương đối với dữ liệu nền. Cả hai không chứng minh nguyên nhân gây bệnh.')
    st.markdown('### Xem lại lần dự đoán gần nhất')
    if st.session_state.get('last_prediction') is not None:
        st.caption('Kết quả đã lưu trong phiên · '+st.session_state.get('last_time','')+' · Nguồn: '+str(st.session_state.get('last_source','Chưa rõ')))
        render_result(st.session_state['last_prediction'],st.session_state['last_case'],context='history')
        st.button('Xóa kết quả đã lưu',on_click=clear_last_result, key='clear_result_explanation',icon=':material/delete_outline:')
    else:
        st.info('Bạn chưa dự đoán trong phiên này. Hãy vào trang Dự đoán để nhập hoặc tải CSV.')
        st.button('Đi đến trang dự đoán',on_click=take_to_prediction)

elif page=='Nghiên cứu':
    heading('GÓC NHÀ NGHIÊN CỨU','Bằng chứng và kết quả mô hình',
            'Các bảng lấy từ hồ sơ nghiên cứu đã khóa theo từng tuần; có thể kiểm tra nguồn và hiểu sự khác biệt giữa TRAIN CV, OOF và VAL.')
    selected=st.segmented_control('Nội dung nghiên cứu',
        ['Tổng quan','So sánh mô hình','Đóng góp & SHAP','Nguồn & kiểm định'],
        key='research_view',default='Tổng quan',selection_mode='single') or 'Tổng quan'
    st.divider()
    try:
        if selected=='Tổng quan':show_research_overview()
        elif selected=='So sánh mô hình':show_research_models()
        elif selected=='Đóng góp & SHAP':show_research_contribution()
        else:research_sources()
    except (OSError, ValueError, KeyError) as exc:
        st.error('Một tài nguyên nghiên cứu bị thiếu hoặc không hợp lệ. Vui lòng khôi phục các tệp trong resource/ và thử lại; dữ liệu mô hình không bị ảnh hưởng.')

st.markdown('<div class="footer">NAFLD Insight · HUIT · Công cụ minh họa nghiên cứu · Không lưu bệnh án · Không sử dụng để quyết định chẩn đoán hoặc điều trị.</div>',unsafe_allow_html=True)
