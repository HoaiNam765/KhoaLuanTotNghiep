"""Clinical input and CSV contract for NAFLD Insight.

No persistent storage, no dataset loading, no training or TEST references.
Batch import is only inference against the frozen Fusion(b) artifacts.
"""
from __future__ import annotations

import csv
import io
import math
from dataclasses import dataclass, field
import re

NUMERIC_CODES = (
    'RIDAGEYR', 'BMXBMI', 'BMXWAIST', 'BMXHIP', 'BPXOSY1', 'BPXODI1',
    'LBXSASSI', 'LBXSATSI', 'LBXSGTSI', 'LBXSTR', 'LBDHDD', 'LBXTC',
    'LBXSGL', 'LBXGH', 'PAD680', 'DR1TKCAL', 'DR1TSUGR', 'DR1TSFAT', 'DR1TFIBE',
)
CATEGORY_CODES = ('RIAGENDR', 'RIDRETH3', 'BPQ020', 'BPQ080', 'GLYCEMIC_HX', 'PAQ650', 'SMOKE_STATUS')
ALL_CODES = NUMERIC_CODES + CATEGORY_CODES

CHOICES = {
    'RIAGENDR': {1: 'Nam', 2: 'Nữ'},
    'RIDRETH3': {1: 'Người Mỹ gốc Mexico', 2: 'Hispanic khác',
                 3: 'Da trắng (không Hispanic)', 4: 'Da đen (không Hispanic)',
                 6: 'Châu Á (không Hispanic)', 7: 'Khác / đa chủng tộc'},
    'BPQ020': {1: 'Có', 2: 'Không'}, 'BPQ080': {1: 'Có', 2: 'Không'},
    'GLYCEMIC_HX': {0: 'Không', 1: 'Tiền đái tháo đường / giới hạn', 2: 'Đái tháo đường'},
    'PAQ650': {1: 'Có', 2: 'Không'},
    'SMOKE_STATUS': {0: 'Chưa từng hút', 1: 'Đã bỏ', 2: 'Thỉnh thoảng', 3: 'Hằng ngày'},
}
GROUP_CODES = {
    'G1': ('RIDAGEYR', 'RIAGENDR', 'RIDRETH3', 'BMXBMI', 'BMXWAIST', 'BMXHIP', 'BPXOSY1', 'BPXODI1'),
    'G2': ('LBXSASSI', 'LBXSATSI', 'LBXSGTSI', 'LBXSTR', 'LBDHDD', 'LBXTC', 'LBXSGL', 'LBXGH'),
    'G3': ('BPQ020', 'BPQ080', 'GLYCEMIC_HX'),
    'G4': ('PAD680', 'PAQ650', 'SMOKE_STATUS', 'DR1TKCAL', 'DR1TSUGR', 'DR1TSFAT', 'DR1TFIBE'),
}
GROUP_TITLES = {'G1': 'Đặc điểm cơ thể', 'G2': 'Kết quả xét nghiệm',
                'G3': 'Tiền sử sức khỏe', 'G4': 'Sinh hoạt và ăn uống'}
NUMERIC_HELP = {
    'RIDAGEYR': 'Tuổi của người được đánh giá, từ 18 đến 80.',
    'BMXBMI': 'Chỉ số khối cơ thể, tính theo kg/m².',
    'BMXWAIST': 'Số đo vòng eo, tính bằng cm; có thể vượt 100 cm.',
    'BMXHIP': 'Số đo vòng mông, tính bằng cm; có thể vượt 100 cm.',
    'BPXOSY1': 'Huyết áp tâm thu, đơn vị mmHg.',
    'BPXODI1': 'Huyết áp tâm trương, đơn vị mmHg.',
    'LBXSASSI': 'AST: enzyme có ở gan và các mô khác; không tự xác nhận gan nhiễm mỡ.',
    'LBXSATSI': 'ALT: enzyme thường được sử dụng trong đánh giá tổn thương tế bào gan.',
    'LBXSGTSI': 'GGT: enzyme liên quan gan và đường mật.',
    'LBXSTR': 'Triglyceride: một loại chất béo trong máu.',
    'LBDHDD': 'HDL-cholesterol: thành phần cholesterol vận chuyển bởi HDL.',
    'LBXTC': 'Cholesterol toàn phần trong máu.',
    'LBXSGL': 'Glucose huyết thanh tại thời điểm lấy mẫu.',
    'LBXGH': 'HbA1c: chỉ số liên quan đường huyết trung bình trong khoảng 2–3 tháng.',
    'PAD680': 'Thời gian ngồi hoặc ít vận động, tính bằng phút mỗi ngày.',
    'DR1TKCAL': 'Năng lượng ăn uống ghi nhận ngày khảo sát thứ nhất.',
    'DR1TSUGR': 'Tổng đường từ khẩu phần ngày khảo sát thứ nhất.',
    'DR1TSFAT': 'Chất béo bão hòa từ khẩu phần ngày khảo sát thứ nhất.',
    'DR1TFIBE': 'Chất xơ từ khẩu phần ngày khảo sát thứ nhất.',
}
CATEGORY_HELP = {
    'RIAGENDR': 'Giới tính theo hai nhóm mã hóa trong dữ liệu NHANES.',
    'RIDRETH3': 'Nhóm chủng tộc/dân tộc của NHANES Hoa Kỳ, không đại diện chắc chắn cho người Việt Nam. Mô hình chưa được kiểm định trên dân số Việt Nam; lựa chọn này có thể làm thay đổi điểm dự đoán.',
    'BPQ020': 'Từng được thông báo/chẩn đoán tăng huyết áp.',
    'BPQ080': 'Từng được thông báo cholesterol cao.',
    'GLYCEMIC_HX': 'Thông tin tiền sử đường huyết; không thay thế HbA1c.',
    'PAQ650': 'Có thực hiện hoạt động thể lực mạnh trong thời gian rảnh theo câu hỏi khảo sát.',
    'SMOKE_STATUS': 'Tình trạng hút thuốc theo nhóm khảo sát.',
}
MAX_FILE_BYTES = 1_000_000
MAX_ROWS = 100

EXAMPLE_A = dict(RIDAGEYR=52, BMXBMI=34.5, BMXWAIST=112, BMXHIP=110,
    BPXOSY1=138, BPXODI1=86, RIAGENDR=1, RIDRETH3=3,
    LBXSASSI=45, LBXSATSI=38, LBXSGTSI=62, LBXSTR=185,
    LBDHDD=38, LBXTC=210, LBXSGL=118, LBXGH=6.1,
    BPQ020=1, BPQ080=1, GLYCEMIC_HX=1, PAD680=480,
    DR1TKCAL=None, DR1TSUGR=None, DR1TSFAT=None, DR1TFIBE=None,
    PAQ650=2, SMOKE_STATUS=1)
EXAMPLE_B = dict(RIDAGEYR=30, BMXBMI=21, BMXWAIST=72, BMXHIP=92,
    BPXOSY1=108, BPXODI1=68, RIAGENDR=2, RIDRETH3=6,
    LBXSASSI=18, LBXSATSI=12, LBXSGTSI=12, LBXSTR=70,
    LBDHDD=65, LBXTC=170, LBXSGL=88, LBXGH=5.2,
    BPQ020=2, BPQ080=2, GLYCEMIC_HX=0, PAD680=240,
    DR1TKCAL=1800, DR1TSUGR=70, DR1TSFAT=20, DR1TFIBE=18,
    PAQ650=1, SMOKE_STATUS=0)

class InputError(ValueError):
    """Invalid user-provided input; safe to show to a user."""


# Phạm vi giá trị quan sát được trong TRAIN khóa, theo 06_DANH_GIA_WEB_V2.md (mục 2.2).
# Chỉ CẢNH BÁO, không tự điều chỉnh giá trị hoặc xem phạm vi là giới hạn y khoa.
TRAIN_RANGES = {
    'BMXBMI':(14.9,86.2), 'BMXWAIST':(56.4,169.5), 'BMXHIP':(74,179),
    'BPXOSY1':(80,224), 'BPXODI1':(42,151),
    'LBXSASSI':(7,294), 'LBXSATSI':(4,213), 'LBXSGTSI':(2,1192),
    'LBXSTR':(25,2923), 'LBDHDD':(5,178), 'LBXTC':(76,431),
    'LBXSGL':(47,626), 'LBXGH':(3.6,14.5), 'PAD680':(1,1320),
}
# Giới hạn kỹ thuật rộng để chặn lỗi đơn vị/nhập sai hiển nhiên, KHÔNG phải ngưỡng chẩn đoán.
HARD_LIMITS = {
    'BMXBMI':(5,120), 'BMXWAIST':(30,300), 'BMXHIP':(30,300),
    'BPXOSY1':(40,320), 'BPXODI1':(15,220),
    'LBXSASSI':(0,10000), 'LBXSATSI':(0,10000),'LBXSGTSI':(0,10000),
    'LBXSTR':(0,10000), 'LBDHDD':(0,1000), 'LBXTC':(0,1500),
    'LBXSGL':(0,1800), 'LBXGH':(2,25), 'PAD680':(0,1440),
    'DR1TKCAL':(0,30000), 'DR1TSUGR':(0,10000), 'DR1TSFAT':(0,10000), 'DR1TFIBE':(0,10000),
}
CORE_BODY_CODES = ('BMXBMI', 'BMXWAIST', 'BMXHIP')
# Khẩu phần tính bằng gam: NHANES ghi tới 3 chữ số lẻ (ví dụ 39.178 g chất béo bão hòa)
# và giá trị lớn nhất trong TRAIN đều dưới 1.000 g, nên 3 biến này không thuộc diện nghi
# dấu phân cách hàng nghìn.
DECIMAL_GRAM_CODES = frozenset({'DR1TSUGR', 'DR1TSFAT', 'DR1TFIBE'})
# Fields whose valid technical range can exceed 999: reject ambiguous grouped
# strings such as 1,200 or 1.200; users must type 1200 or a clear decimal.
AMBIGUOUS_THOUSANDS_FIELDS = frozenset(
    code for code, (_, upper) in HARD_LIMITS.items()
    if upper > 999 and code not in DECIMAL_GRAM_CODES
)

FIELD_NAMES = {
    'RIDAGEYR':'Tuổi', 'BMXBMI':'BMI', 'BMXWAIST':'Vòng eo', 'BMXHIP':'Vòng mông',
    'BPXOSY1':'Huyết áp tâm thu', 'BPXODI1':'Huyết áp tâm trương',
    'RIAGENDR':'Giới tính', 'RIDRETH3':'Chủng tộc / dân tộc',
    'LBXSASSI':'AST', 'LBXSATSI':'ALT', 'LBXSGTSI':'GGT', 'LBXSTR':'Triglyceride',
    'LBDHDD':'HDL-cholesterol', 'LBXTC':'Cholesterol toàn phần', 'LBXSGL':'Glucose',
    'LBXGH':'HbA1c', 'BPQ020':'Tiền sử tăng huyết áp', 'BPQ080':'Tiền sử cholesterol cao',
    'GLYCEMIC_HX':'Tiền sử đường huyết', 'PAQ650':'Vận động mạnh', 'SMOKE_STATUS':'Hút thuốc',
    'PAD680':'Thời gian ngồi', 'DR1TKCAL':'Năng lượng khẩu phần', 'DR1TSUGR':'Đường khẩu phần',
    'DR1TSFAT':'Chất béo bão hòa', 'DR1TFIBE':'Chất xơ',
}
OPTIONAL_CATEGORIES = frozenset({'BPQ020','BPQ080','GLYCEMIC_HX','PAQ650','SMOKE_STATUS'})

def numeric_value(value, field):
    """Phân tích số, phát hiện sai đơn vị quá rõ; không thay đổi mô hình/phép chuẩn hóa."""
    if value is None or str(value).strip().lower() in ('', 'nan', 'null', 'n/a', 'na'):
        if field == 'RIDAGEYR':
            raise InputError('Tuổi là thông tin bắt buộc (18–80).')
        return None
    raw_text = str(value).strip()
    if field in AMBIGUOUS_THOUSANDS_FIELDS and re.fullmatch(r'\d{1,3}(?:[,.]\d{3})+',raw_text):
        raise InputError(f'{FIELD_NAMES[field]}: cách viết {raw_text} có thể bị hiểu nhầm là dấu phân cách hàng nghìn hoặc dấu thập phân. Hãy nhập số thập phân với phần lẻ rõ ràng (ví dụ 1,2) hoặc số nguyên không có dấu phân tách (ví dụ 1200). Hệ thống không tự chuyển đổi.')
    try:
        result = float(raw_text.replace(',', '.'))
    except (ValueError, TypeError):
        raise InputError(f'{FIELD_NAMES[field]}: vui lòng nhập số hợp lệ.') from None
    if not math.isfinite(result) or result < 0 or result > 100000:
        raise InputError(f'{FIELD_NAMES[field]}: giá trị không hợp lệ.')
    if field == 'RIDAGEYR' and (not result.is_integer() or not 18 <= result <= 80):
        raise InputError('Tuổi phải là số nguyên từ 18 đến 80.')
    if field == 'PAD680':
        if 0 <= result < 1e-10:
            result=0.0  # SAS ghi số 0 thành giá trị vô cùng nhỏ (ví dụ 5.397605e-79).
        if result in (7777,9999):
            return None  # NHANES: không biết / từ chối trả lời
        if not result.is_integer():
            raise InputError('Thời gian ngồi phải nhập bằng số phút nguyên.')
    if field in HARD_LIMITS:
        low, high = HARD_LIMITS[field]
        if not low <= result <= high:
            raise InputError(f'{FIELD_NAMES[field]}: {result:g} nằm ngoài giới hạn kiểm tra hợp lý ({low:g}–{high:g}); hãy kiểm tra lại đơn vị và số liệu. Đây không phải ngưỡng y khoa.')
    return int(result) if field in ('RIDAGEYR', 'PAD680') else result


def category_value(value, field):
    choices = CHOICES[field]
    if value is None or str(value).strip().lower() in ('', 'nan', 'null', 'không rõ', 'khong ro'):
        if field in OPTIONAL_CATEGORIES:
            return None  # Imputer đã fit từ TRAIN tiếp tục xử lý như pipeline nghiên cứu.
        raise InputError(f'{FIELD_NAMES[field]}: hãy chọn một giá trị danh mục.')
    text = str(value).strip()
    try:
        numerical = float(text.replace(',', '.'))
        if numerical.is_integer() and int(numerical) in choices:
            return int(numerical)
    except ValueError:
        pass
    for code, description in choices.items():
        if text.casefold() == description.casefold():
            return code
    raise InputError(f'{FIELD_NAMES[field]}: mã không hợp lệ; sử dụng mã hoặc nhãn trong tệp mẫu.')


def validate_case(raw):
    """Return 26 canonical fields; avoid untrustworthy input before frozen preprocessing."""
    result = {}
    errors = []
    for field in NUMERIC_CODES:
        try:
            result[field] = numeric_value(raw.get(field), field)
        except InputError as exc:
            errors.append(str(exc))
    for field in CATEGORY_CODES:
        try:
            result[field] = category_value(raw.get(field), field)
        except InputError as exc:
            errors.append(str(exc))
    a,b = result.get('BPXOSY1'),result.get('BPXODI1')
    if a is not None and b is not None and a <= b:
        errors.append('Huyết áp tâm thu cần lớn hơn huyết áp tâm trương; kiểm tra lại thứ tự nhập (mmHg).')
    if errors:
        raise InputError(' '.join(errors))
    return result


def core_measurement_extrapolations(case):
    """Return G1 body measurements outside the observed TRAIN range."""
    flagged = []
    for code in CORE_BODY_CODES:
        value = case.get(code)
        low, high = TRAIN_RANGES[code]
        if value is not None and not low <= value <= high:
            flagged.append((code, float(value), low, high))
    return flagged


def input_warnings(case):
    """Transparent warnings based on original TRAIN, not clinical verdicts."""
    warnings=[]
    core_codes = set(CORE_BODY_CODES)
    for code,(low,high) in TRAIN_RANGES.items():
        value=case.get(code)
        if value is not None and not low <= value <= high:
            if code in core_codes:
                warnings.append(f'{FIELD_NAMES[code]}: {value:g} nằm ngoài khoảng quan sát trong TRAIN ({low:g}–{high:g}); mô hình đang ngoại suy và cần được diễn giải thận trọng.')
            else:
                warnings.append(f'{FIELD_NAMES[code]}: {value:g} nằm ngoài khoảng quan sát trong TRAIN ({low:g}–{high:g}).')
    for code,upper in [('LBXSTR',15),('LBXSGL',30),('LBDHDD',4),('LBXTC',40)]:
        value=case.get(code)
        if value is not None and 0 < value < upper:
            warnings.append(f'{FIELD_NAMES[code]}: đang yêu cầu mg/dL; giá trị này có thể do nhập mmol/L. KHÔNG tự đổi đơn vị.')
    missing=[c for c in NUMERIC_CODES if case.get(c) is None]
    if missing:
        warnings.append(f'Đang thiếu {len(missing)}/19 số đo; các trường trống được điền bằng tham số đã học từ TRAIN. Kết quả có thể chịu ảnh hưởng bởi số lượng thông tin còn thiếu.')
    if all(case.get(c) is None for c in CORE_BODY_CODES):
        warnings.append('CẢNH BÁO MẠNH: thiếu đồng thời BMI, vòng eo và vòng mông (ba tín hiệu nhân trắc quan trọng); kết quả có thể kém tin cậy.')
    if any(case.get(c) is None for c in OPTIONAL_CATEGORIES):
        warnings.append('Một số thông tin bệnh nền/lối sống chọn “Không rõ”; mô hình điền thiếu bằng quy tắc đã học từ TRAIN.')
    return warnings


def csv_template():
    """UTF-8 BOM for Excel; two synthetic examples (never VAL/TEST records)."""
    output = io.StringIO(newline='')
    writer = csv.DictWriter(output, fieldnames=ALL_CODES, delimiter=',', lineterminator='\n')
    writer.writeheader()
    for example in (EXAMPLE_A, EXAMPLE_B):
        writer.writerow({code: '' if example.get(code) is None else example[code] for code in ALL_CODES})
    return ('\ufeff' + output.getvalue()).encode('utf-8')


@dataclass
class CsvValidation:
    rows: list[dict]
    errors: dict[int, str]
    extra_columns: list[str]
    row_numbers: list[int] = field(default_factory=list)


def parse_csv_bytes(payload):
    if not isinstance(payload, (bytes, bytearray)) or len(payload) > MAX_FILE_BYTES:
        raise InputError('Tệp phải là CSV UTF-8, dung lượng không vượt 1 MB.')
    try:
        contents = bytes(payload).decode('utf-8-sig')
    except UnicodeDecodeError:
        raise InputError('CSV cần mã hóa UTF-8. Hãy lưu dưới dạng CSV UTF-8 trong Excel.') from None
    first_line = contents.splitlines()[0] if contents.splitlines() else ''
    delimiter = ';' if first_line.count(';') > first_line.count(',') else ','
    reader = csv.DictReader(io.StringIO(contents, newline=''), delimiter=delimiter)
    if reader.fieldnames is None:
        raise InputError('Không tìm thấy hàng tiêu đề CSV.')
    cols = [c.strip() if c is not None else '' for c in reader.fieldnames]
    if len(set(cols)) != len(cols) or any(not c for c in cols):
        raise InputError('Tiêu đề CSV trùng hoặc rỗng.')
    missing = [code for code in ALL_CODES if code not in cols]
    if missing:
        raise InputError('CSV thiếu cột bắt buộc: ' + ', '.join(missing))
    extra = [code for code in cols if code not in ALL_CODES]
    rows, errors, row_numbers = [], {}, []
    for values in reader:
        line = reader.line_num
        if len(rows) >= MAX_ROWS:
            raise InputError(f'Mỗi lần chỉ nhập tối đa {MAX_ROWS} dòng. Vui lòng chia nhỏ tệp.')
        if None in values:
            raise InputError(f'Dòng {line}: số ô lớn hơn số cột tiêu đề; kiểm tra dấu phân cách CSV.')
        item = {str(k).strip(): v for k, v in values.items()}
        row_numbers.append(line)
        try:
            rows.append(validate_case(item))
        except InputError as exc:
            rows.append(item)
            errors[line] = str(exc)
    if not rows:
        raise InputError('Tệp CSV không có dòng dữ liệu.')
    return CsvValidation(rows=rows, errors=errors, extra_columns=extra, row_numbers=row_numbers)


def batch_predict(parsed, predict_fn):
    """Run inference for valid rows only; never include original patient inputs in exports."""
    records = []
    cases = {}
    for row_number, case in zip(parsed.row_numbers or list(range(2,2+len(parsed.rows))), parsed.rows):
        if row_number in parsed.errors:
            records.append({'Dòng CSV':row_number, 'Xác suất (%)':None,
                            'Kết luận':'Không hợp lệ', 'Chi tiết lỗi':parsed.errors[row_number], 'Ngưỡng F1 OOF (%)':None, 'Mô hình':'Fusion (b) seed 42'})
            continue
        try:
            result = predict_fn(case, 'F1 OOF')
            cases[row_number] = (case, result)
            records.append({'Dòng CSV':row_number, 'Xác suất (%)':round(result['probability']*100,2),
                            'Kết luận':'Trên ngưỡng nguy cơ nghiên cứu' if result['positive'] else 'Dưới ngưỡng nguy cơ nghiên cứu',
                            'Ngưỡng F1 OOF (%)':round(result['threshold']*100,2),'Mô hình':'Fusion (b) seed 42',
                            'Chi tiết lỗi':''})
        except Exception:
            records.append({'Dòng CSV':row_number, 'Xác suất (%)':None,
                            'Kết luận':'Lỗi suy luận', 'Chi tiết lỗi':'Không thể suy luận dòng này bằng mô hình đã khóa.', 'Ngưỡng F1 OOF (%)':None, 'Mô hình':'Fusion (b) seed 42'})
    return records, cases


def csv_columns_guide(labels):
    """User-facing dictionary; label metadata belongs to frozen research resource."""
    output=[]
    for code in ALL_CODES:
        label,unit=labels.get(code,(code,''))
        allowed=' / '.join(f'{k} = {v}' for k,v in CHOICES[code].items()) if code in CHOICES else ''
        output.append({'Mã cột':code,'Tên thông tin':label,'Đơn vị':unit,
                       'Bắt buộc':'Có' if code in ('RIDAGEYR','RIAGENDR','RIDRETH3') else 'Không',
                       'Giá trị danh mục cho phép':allowed + (' / Không rõ = bỏ trống' if code in OPTIONAL_CATEGORIES else '')})
    return output
