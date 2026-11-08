"""Run: python scripts/kiem_tra_anh.py (from any working directory)."""
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.branding import candidate_brand_paths, inspect_static_image

NAMES = {'logo': 'logo.png', 'cover': 'cover.png', 'research': 'research.png'}


def main():
    print(f'Dự án: {ROOT_DIR}')
    print('Ưu tiên ảnh trong app/assets/. Cũng tìm trong assets/, app/asset/, asset/.\n')
    missing = 0
    for label, filename in NAMES.items():
        primary = ROOT_DIR / 'app' / 'assets' / filename
        locations = candidate_brand_paths(primary, ROOT_DIR)
        selected = None
        print(f'[{label}]')
        for path in locations:
            data, status = inspect_static_image(path)
            print(f' - {path.relative_to(ROOT_DIR)}: {status}')
            if data is not None and selected is None:
                selected = path
        if selected:
            print(f' => SẼ HIỂN THỊ: {selected.relative_to(ROOT_DIR)}')
        else:
            missing += 1
            near = []
            for base in {p.parent for p in locations}:
                if base.exists():
                    near += [str(x.relative_to(ROOT_DIR)) for x in base.iterdir() if x.is_file() and x.name.lower().startswith(label)]
            if near:
                print(' => Tệp tên gần giống:', ', '.join(sorted(set(near))))
            print(f' => KHÔNG HIỂN THỊ: đặt ảnh đúng tên {filename}')
        print()
    if missing:
        print(f'{missing}/3 ảnh chưa hợp lệ. Xem các dòng lỗi ở trên.')
        return 1
    print('Cả 3 ảnh hợp lệ. Khởi động lại Streamlit và nhấn Ctrl+F5.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
