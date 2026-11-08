from pathlib import Path
from io import BytesIO
from PIL import Image

from src.branding import load_brand_image, inspect_static_image, image_to_data_uri, candidate_brand_paths


def test_jpeg_with_png_file_name_loads_and_sets_correct_mime(tmp_path):
    img = tmp_path / 'logo.png'
    Image.new('RGB', (180, 180), 'blue').save(img, format='JPEG')
    data, status = inspect_static_image(img)
    assert data is not None
    assert 'JPEG' in status
    assert image_to_data_uri(data).startswith('data:image/jpeg;base64,')


def test_fallback_root_assets_is_found(tmp_path):
    path = tmp_path / 'assets' / 'cover.png'
    path.parent.mkdir()
    Image.new('RGB', (180, 80), 'blue').save(path)
    data = load_brand_image(tmp_path / 'app/assets/cover.png', tmp_path)
    assert data is not None
    assert candidate_brand_paths(tmp_path/'app/assets/cover.png', tmp_path)[1] == path


def test_missing_and_invalid_are_reported(tmp_path):
    path = tmp_path / 'logo.png'
    assert inspect_static_image(path)[0] is None
    path.write_text('not image', encoding='utf-8')
    data, status = inspect_static_image(path)
    assert data is None and 'không đọc' in status.lower()


def test_header_and_research_not_changed():
    root = Path(__file__).resolve().parents[1]
    src = (root / 'app/app.py').read_text(encoding='utf-8')
    assert 'load_brand_image(BRAND_IMAGE_PATHS[kind], ROOT_DIR)' in src
    assert 'st.file_uploader' in src
    assert "brand_image_bytes('logo')" in src
    assert "brand_image_bytes('cover')" in src
    assert "brand_image_bytes('research')" in src
