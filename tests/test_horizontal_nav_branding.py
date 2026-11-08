"""Check horizontal navigation and local-only fixed brand image assets."""
from pathlib import Path
import io

from PIL import Image

from src.branding import image_to_data_uri, load_static_png

ROOT = Path(__file__).resolve().parents[1]


def make_png(path, size=(200, 100)):
    Image.new('RGB', size, '#176a72').save(path, format='PNG')


def test_missing_static_image_returns_none(tmp_path):
    assert load_static_png(tmp_path / 'missing.png') is None


def test_fixed_png_loads_and_creates_data_uri(tmp_path):
    p = tmp_path / 'logo.png'
    make_png(p)
    image = load_static_png(p)
    assert image is not None
    assert image_to_data_uri(image).startswith('data:image/png;base64,')


def test_invalid_or_oversized_fixed_image_uses_fallback(tmp_path):
    invalid = tmp_path / 'logo.png'
    invalid.write_bytes(b'<svg><script>invalid</script></svg>')
    assert load_static_png(invalid) is None
    invalid.write_bytes(b'0' * 8_000_001)
    assert load_static_png(invalid) is None


def test_navigation_has_no_image_upload_but_keeps_csv_upload():
    code = (ROOT / 'app/app.py').read_text(encoding='utf-8')
    assert 'site_header()' in code
    assert 'navbar = st.columns(4' in code
    assert 'st.button(label, icon=icon' in code
    assert 'with st.sidebar:' not in code
    assert "'logo': BRAND_ASSETS / 'logo.png'" in code
    assert "'cover': BRAND_ASSETS / 'cover.png'" in code
    assert "'research': BRAND_ASSETS / 'research.png'" in code
    assert 'brand_upload_control' not in code
    assert "st.popover('Ảnh & nhận diện'" not in code
    assert "st.file_uploader('Chọn tệp CSV UTF-8'" in code
    assert 'result=predict_case(case,DEFAULT_MODE)' in code
