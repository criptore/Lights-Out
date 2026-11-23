"""Freeze the final models before looking at the test storms.

For each final model (classifier, regression setups A and B) this script:
  1. rebuilds the same data, features and storm-level train/test split as
     notebooks 02 and 03 (same seed, same GroupShuffleSplit);
  2. re-runs the 5-fold cross-validation split by storm on the training storms
     with the chosen hyperparameters, which gives the expected validation score;
  3. fits the model on all training storms and saves it to models/;
  4. writes the SHA-256 hash of the saved model file next to its config in
     results/classifier_final_model.json and results/regression_final_model.json.

The test storms are only used at the end, to check that the frozen model gives
the same test score as the notebooks (the score is not used to pick anything).

Run from the repository root:  python scripts/freeze_models.py
Check the saved files later:    python scripts/freeze_models.py --check
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import sklearn
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingRegressor, RandomForestClassifier, RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error, r2_score, roc_auc_score
from sklearn.model_selection import GroupKFold, GroupShuffleSplit, cross_validate
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder

ROOT = Path(__file__).resolve().parent.parent
DATA, RES, MODELS = ROOT / 'data', ROOT / 'results', ROOT / 'models'
SEED = 0
CAT = ['kind', 'state', 'wind_radius']
NUM_A = ['year', 'month', 'log_customers', 'log_baseline']
NUM_B = NUM_A + ['log_peak', 'peak_share_out']
CV = GroupKFold(n_splits=5)


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def load():
    storms = pd.read_csv(DATA / 'storms.csv')
    utility = pd.read_csv(DATA / 'utility_by_county.csv', low_memory=False)
    county = pd.read_csv(DATA / 'county_summary.csv', low_memory=False,
                         usecols=['event_id', 'geoid', 'in_nhc_wind_radius', 'baseline_radiance'])
    storms['date'] = pd.to_datetime(storms['landfall'].fillna(storms['first_impact_date']), errors='coerce')
    storms['year'] = storms['date'].dt.year
    storms['month'] = storms['date'].dt.month
    df = (utility.merge(storms[['event_id', 'name', 'kind', 'year', 'month']], on='event_id', how='left')
                 .merge(county, on=['event_id', 'geoid'], how='left'))
    df = df[df['reason'] == 'ok'].copy()
    df['log_customers'] = np.log1p(df['customers_total'])
    df['log_baseline'] = np.log1p(df['baseline_radiance'])
    df['log_peak'] = np.log1p(df['peak_customers_out'])
    df['wind_radius'] = (df['in_nhc_wind_radius'].astype('string').str.lower()
                           .map({'true': 'inside', 'false': 'outside'}).fillna('unknown'))
    return df


def split(X, y, groups):
    outer = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=SEED)
    return next(outer.split(X, y, groups))


def onehot_rf(model, num):
    pre = ColumnTransformer([
        ('cat', OneHotEncoder(handle_unknown='ignore', min_frequency=20, sparse_output=False), CAT),
        ('num', SimpleImputer(strategy='median'), num)])
    return make_pipeline(pre, model)


def ordinal(model, num):
    pre = ColumnTransformer([
        ('cat', OrdinalEncoder(handle_unknown='use_encoded_value', unknown_value=-1, encoded_missing_value=-1), CAT),
        ('num', 'passthrough', num)])
    return make_pipeline(pre, model)


def save(model, name):
    MODELS.mkdir(exist_ok=True)
    path = MODELS / f'{name}.joblib'
    joblib.dump(model, path, compress=3)
    return path


def freeze_classifier(full):
    df = full[full['peak_share_out'].notna()].copy()
    X = df[CAT + NUM_A]
    y = (df['peak_share_out'] > 0.10).astype(int).to_numpy()
    groups = df['event_id'].to_numpy()
    tr, te = split(X, y, groups)

    config = json.loads((RES / 'classifier_final_model.json').read_text())
    params = {k: config[k] for k in ('max_features', 'min_samples_leaf')}
    model = onehot_rf(RandomForestClassifier(n_estimators=300, n_jobs=-1, random_state=SEED, **params), NUM_A)

    folds = cross_validate(model, X.iloc[tr], y[tr], groups=groups[tr], cv=CV, scoring='roc_auc', n_jobs=-1)['test_score']
    model.fit(X.iloc[tr], y[tr])
    path = save(model, 'classifier')
    test_auc = roc_auc_score(y[te], model.predict_proba(X.iloc[te])[:, 1])

    for label, ours, theirs in [('CV AUC', folds.mean(), config['cv_auc_mean']), ('test AUC', test_auc, config['test_auc'])]:
        print(f'classifier  {label:9s} {ours:.4f}  (notebook 02: {theirs:.4f})')
    config.update({
        'n_estimators': 300, 'random_state': SEED,
        'features': CAT + NUM_A, 'target': 'peak_share_out > 0.10',
        'train_rows': int(len(tr)), 'train_storms': int(len(set(groups[tr]))),
        'cv_auc_folds': [round(float(s), 4) for s in folds],
        'model_file': path.relative_to(ROOT).as_posix(),
        'model_sha256': sha256(path),
        'scikit_learn': sklearn.__version__,
    })
    (RES / 'classifier_final_model.json').write_text(json.dumps(config, indent=1) + '\n')


def freeze_regression(full):
    df = full[full['hours_to_90pct_restored'].notna()].copy()
    df['log_hours'] = np.log1p(df['hours_to_90pct_restored'])
    X = df[CAT + NUM_B]
    y = df['log_hours'].to_numpy()
    groups = df['event_id'].to_numpy()
    tr, te = split(X, y, groups)

    chosen = json.loads((RES / 'regression_summary.json').read_text())['final_models']
    test_ref = pd.read_csv(RES / 'regression_test_metrics.csv', index_col='model')
    builders = {
        'Random forest': lambda p, num: onehot_rf(RandomForestRegressor(
            n_estimators=300, n_jobs=-1, random_state=SEED,
            min_samples_leaf=p['min_samples_leaf'], max_features=p['max_features']), num),
        'Gradient boosting': lambda p, num: ordinal(HistGradientBoostingRegressor(
            categorical_features=[0, 1, 2], random_state=SEED,
            learning_rate=p['learning_rate'], max_leaf_nodes=p['max_leaf_nodes'],
            l2_regularization=p['l2_regularization']), num),
    }
    tuned = {'Random forest': ('min_samples_leaf', 'max_features'),
             'Gradient boosting': ('learning_rate', 'max_leaf_nodes', 'l2_regularization')}

    out = {'target': 'log(1 + hours_to_90pct_restored)', 'cv': '5-fold GroupKFold by storm on the training storms',
           'selection_metric': 'mean CV R2 (log hours)', 'setups': {}}
    for setup, num in [('A', NUM_A), ('B', NUM_B)]:
        name = chosen[setup]['model']
        params = {k: chosen[setup][k] for k in tuned[name]}
        model = builders[name](params, num)
        cols = CAT + num
        s = cross_validate(model, X.iloc[tr][cols], y[tr], groups=groups[tr], cv=CV, n_jobs=-1,
                           scoring={'r2': 'r2', 'mae': 'neg_mean_absolute_error'})
        model.fit(X.iloc[tr][cols], y[tr])
        path = save(model, f'regression_{setup}')
        pred = model.predict(X.iloc[te][cols])
        ref = test_ref.loc[f'{setup}: {name}']
        print(f'regression {setup} {name:17s} CV R2 {s["test_r2"].mean():.4f}   test R2 {r2_score(y[te], pred):.4f}'
              f'  (notebook 03: {ref["R2 (log)"]:.4f})')
        mae = -s['test_mae'].mean()
        out['setups'][setup] = {
            'model': name, **params,
            'n_estimators': 300 if name == 'Random forest' else None,
            'random_state': SEED,
            'features': cols,
            'train_rows': int(len(tr)), 'train_storms': int(len(set(groups[tr]))),
            'cv_r2_mean': round(float(s['test_r2'].mean()), 4),
            'cv_r2_std': round(float(s['test_r2'].std()), 4),
            'cv_r2_folds': [round(float(v), 4) for v in s['test_r2']],
            'cv_mae_log': round(float(mae), 4),
            'cv_error_factor': round(float(np.exp(mae)), 4),
            'test_r2': round(float(r2_score(y[te], pred)), 4),
            'test_mae_log': round(float(mean_absolute_error(y[te], pred)), 4),
            'model_file': path.relative_to(ROOT).as_posix(),
            'model_sha256': sha256(path),
        }
        if name != 'Random forest':
            del out['setups'][setup]['n_estimators']
    out['scikit_learn'] = sklearn.__version__
    (RES / 'regression_final_model.json').write_text(json.dumps(out, indent=1) + '\n')


def check():
    entries = []
    c = json.loads((RES / 'classifier_final_model.json').read_text())
    entries.append(('classifier', c))
    r = json.loads((RES / 'regression_final_model.json').read_text())
    entries += [(f'regression {k}', v) for k, v in r['setups'].items()]
    ok = True
    for label, e in entries:
        path = ROOT / e['model_file']
        good = path.exists() and sha256(path) == e['model_sha256']
        ok &= good
        print(f'{label:13s} {e["model_file"]:30s} {"OK" if good else "HASH MISMATCH OR MISSING"}')
    return ok


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true', help='only check the saved models against their hashes')
    args = parser.parse_args()
    if args.check:
        sys.exit(0 if check() else 1)
    full = load()
    freeze_classifier(full)
    freeze_regression(full)
    check()
