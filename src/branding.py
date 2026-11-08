"""Read local, fixed NAFLD Insight brand images (never browser uploads)."""
from __future__ import annotations

import base64
import io
from pathlib import Path

from PIL import Image, UnidentifiedImageError

MAX_IMAGE_BYTES = 8_000_000
MAX_PIXELS = 20_000_000
IMAGE_FORMATS = {"PNG": "image/png", "JPEG": "image/jpeg", "WEBP": "image/webp"}


def inspect_static_image(path: Path) -> tuple[bytes | None, str]:
    """Return validated bytes and a human-readable status for troubleshooting."""
    path = Path(path)
    try:
        if not path.is_file():
            return None, "Không tìm thấy tệp"
        size = path.stat().st_size
        if size == 0:
            return None, "Tệp rỗng"
        if size > MAX_IMAGE_BYTES:
            return None, f"Ảnh vượt 8 MB ({size / 1_000_000:.2f} MB)"
        raw = path.read_bytes()
        with Image.open(io.BytesIO(raw)) as picture:
            if picture.format not in IMAGE_FORMATS:
                return None, f"Định dạng {picture.format} không được hỗ trợ; dùng PNG, JPG hoặc WebP"
            fmt = picture.format
            width, height = picture.size
            if width * height > MAX_PIXELS:
                return None, f"Ảnh quá lớn: {width}×{height} (>20 triệu pixel)"
            picture.verify()
        return raw, f"OK – {fmt}, {width}×{height}, {size:,} byte"
    except (OSError, ValueError, UnidentifiedImageError, Image.DecompressionBombError, SyntaxError) as exc:
        return None, f"Ảnh không đọc được ({type(exc).__name__})"


def load_static_image(path: Path) -> bytes | None:
    """Read valid PNG/JPEG/WebP from a path configured in source code."""
    return inspect_static_image(path)[0]


def load_static_png(path: Path) -> bytes | None:
    """Backward-compatible PNG-only loader used by existing tests."""
    raw = load_static_image(path)
    if raw is None:
        return None
    with Image.open(io.BytesIO(raw)) as picture:
        return raw if picture.format == 'PNG' else None


def candidate_brand_paths(primary: Path, root: Path) -> list[Path]:
    """Known local asset folders. The configured path always has priority."""
    result = [Path(primary)]
    for rel in ('app/assets', 'assets', 'app/asset', 'asset'):
        candidate = Path(root) / rel / primary.name
        if candidate not in result:
            result.append(candidate)
    return result


def load_brand_image(primary: Path, root: Path) -> bytes | None:
    for path in candidate_brand_paths(primary, root):
        raw = load_static_image(path)
        if raw is not None:
            return raw
    return None


def image_to_data_uri(raw: bytes) -> str:
    """Embed a validated local image in the existing HTML header/cover."""
    with Image.open(io.BytesIO(raw)) as picture:
        mime = IMAGE_FORMATS.get(picture.format)
    if mime is None:
        raise ValueError('Only PNG, JPEG, and WebP are supported')
    return f'data:{mime};base64,' + base64.b64encode(raw).decode('ascii')
