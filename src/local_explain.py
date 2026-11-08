"""Giải thích cục bộ ước lượng bằng lấy mẫu hoán vị Shapley.

Chỉ đọc 12 trường hợp VAL đóng băng và các artifact đã khóa. Không dùng TRAIN/TEST,
không cập nhật mô hình, không thay đổi cách tính xác suất dự đoán.

Bản đồ 26 biến gốc -> 43 đặc trưng được nhóm để các mức one-hot, cờ thiếu
đồng hành cùng biến gốc khi hoán vị. Trả đóng góp theo *điểm xác suất*.
"""
from pathlib import Path
import numpy as np
import pandas as pd
from .inference import ROOT, load_runtime, prepare_features

VAL_BACKGROUND = ROOT / 'artifacts' / 'local_explain_background_val12.csv'


def input_feature_groups(bundle):
    """Tạo 26 nhóm của 43 đặc trưng từ các cấu hình tiền xử lý đã khóa."""
    feature_order = list(bundle['feature_order'])
    variables = (list(bundle['numeric_vars']) + list(bundle['binary_mappings'])
                 + list(bundle['multi_categorical_vars']))
    mapping = {}
    for variable in variables:
        names = []
        if variable in feature_order:
            names.append(variable)
        names.extend(c for c in feature_order if c.startswith(variable + '_')
                     and (c in bundle['onehot_columns'] or c.endswith('_was_missing')))
        if variable == 'DR1TKCAL' and 'diet_recall_missing' in feature_order:
            names.append('diet_recall_missing')
        if not names:
            raise RuntimeError(f'Không có đặc trưng được ánh xạ: {variable}')
        mapping[variable] = names
    counts = [col for cols in mapping.values() for col in cols]
    if len(variables) != 26 or len(feature_order) != 43 or sorted(counts) != sorted(feature_order):
        raise RuntimeError('Ánh xạ 26 biến gốc / 43 đặc trưng không đầy đủ hoặc trùng.')
    return mapping


def predict_fusion_batch(features, bundle, groups, weights, models):
    """Dự đoán song song chính xác Fusion(b) trên không gian 43 đặc trưng raw."""
    columns = list(bundle['feature_order'])
    frame = pd.DataFrame(np.asarray(features, dtype=float), columns=columns)
    scaled = frame.copy()
    numeric_cols = list(bundle['numeric_vars'])
    scaled[numeric_cols] = bundle['scaler'].transform(scaled[numeric_cols])
    combined = np.zeros(len(frame), dtype=float)
    for group, model in models.items():
        data = (scaled if group in ('G1','G4') else frame)[groups[group]]
        combined += float(weights[group]) * model.predict_proba(data)[:, 1]
    return combined


def explain_preprocessed(plain, bundle, groups, weights, models, reference=None,
                         n_permutations=12, random_state=42):
    """Ước lượng Shapley theo hoán vị trên 26 nhóm biến đầu vào.

    Mean background = 12 bản ghi VAL đã tiền xử lý. Mỗi hoán vị thay từng nhóm
    đặc trưng bằng giá trị ca được giải thích; hiệu số xác suất được cộng dồn.
    Đẳng thức baseline + Σ đóng góp = p(ca) đúng theo thuật toán telescoping.
    """
    cols = list(bundle['feature_order'])
    if reference is None:
        reference = pd.read_csv(VAL_BACKGROUND)
    if list(reference.columns) != cols:
        raise RuntimeError('Thứ tự cột VAL tham chiếu không khớp 43 đặc trưng.')
    if list(plain.columns) != cols or len(plain) != 1:
        raise ValueError('Dữ liệu ca giải thích phải có đúng 1 hàng và 43 cột đúng thứ tự.')
    if not 1 <= n_permutations <= 64:
        raise ValueError('Số hoán vị không hợp lệ.')

    mapping = input_feature_groups(bundle)
    var_names = list(mapping)
    locations = [np.array([cols.index(col) for col in mapping[name]], dtype=int) for name in var_names]
    bg = reference.to_numpy(dtype=float)
    target = plain.iloc[0].to_numpy(dtype=float)
    rng = np.random.default_rng(random_state)
    n_variables = len(var_names)
    n_ref = len(bg)
    paths = np.empty((n_permutations, n_ref, n_variables+1, len(cols)), dtype=float)
    permutations = []
    for turn in range(n_permutations):
        perm = rng.permutation(n_variables) if turn % 2 == 0 else permutations[-1][::-1]
        permutations.append(perm)
        current = bg.copy()
        paths[turn, :, 0, :] = current
        for j, group_index in enumerate(perm):
            idxs = locations[group_index]
            current[:, idxs] = target[idxs]
            paths[turn, :, j+1, :] = current

    # Mô hình được giữ nguyên; chỉ tạo các đầu vào giả lập từ VAL đã xử lý.
    pred = predict_fusion_batch(paths.reshape(-1,len(cols)),bundle,groups,weights,models)
    pred = pred.reshape(n_permutations,n_ref,n_variables+1)
    contributions = np.zeros(n_variables, dtype=float)
    for i, perm in enumerate(permutations):
        differences = np.mean(pred[i, :, 1:] - pred[i, :, :-1], axis=0)
        contributions[perm] += differences / n_permutations
    baseline = float(np.mean(pred[0,:,0]))
    probability = float(np.mean(pred[0,:,-1]))
    if not np.isfinite(contributions).all() or abs(baseline + sum(contributions) - probability) > 1e-9:
        raise RuntimeError('Giải thích cục bộ không thỏa đẳng thức tổng đóng góp.')
    return {'baseline':baseline,'probability':probability,'contributions':dict(zip(var_names,contributions)),
            'reference_n':n_ref,'permutations':n_permutations,
            'method':'Permutation Shapley (interventional, theo 26 nhóm biến gốc)'}


def explain_case(case, n_permutations=12):
    bundle,groups,weights,_,models = load_runtime()
    plain,_ = prepare_features(case,bundle)
    return explain_preprocessed(plain,bundle,groups,weights,models,n_permutations=n_permutations)
