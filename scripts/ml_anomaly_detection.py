import sys, os, io
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor
from sklearn.preprocessing import StandardScaler
from sqlalchemy import create_engine
import warnings
warnings.filterwarnings('ignore')

DB_URL = os.environ.get('ANALYTICS_DB_URL', 'postgresql+psycopg2://dbt_user:dbt_pass@localhost:5432/analytics')
CSV_PATH = '/opt/analytics/data/test_dataset.csv'

def load_data():
    df = pd.read_csv(CSV_PATH)
    df.columns = [c.strip().lower() for c in df.columns]
    return df

def prepare_features(df):
    numeric_cols = [
        'revenue', 'cost_of_goods', 'gross_profit', 'opex',
        'operating_profit', 'net_profit', 'taxes_paid', 'headcount',
        'payroll_fund', 'dividends_paid'
    ]
    features = df[numeric_cols].fillna(0).values
    scaler = StandardScaler()
    return scaler.fit_transform(features), numeric_cols

def detect_anomalies(features_scaled):
    iso = IsolationForest(n_estimators=100, contamination=0.05, random_state=42, n_jobs=-1)
    iso_preds = iso.fit_predict(features_scaled)
    iso_scores = iso.score_samples(features_scaled)

    lof = LocalOutlierFactor(n_neighbors=20, contamination=0.05, novelty=False, n_jobs=-1)
    lof_preds = lof.fit_predict(features_scaled)

    iso_anomaly = (iso_preds == -1).astype(int)
    lof_anomaly = (lof_preds == -1).astype(int)
    ensemble = ((iso_anomaly + lof_anomaly) >= 1).astype(int)
    return iso_anomaly, lof_anomaly, ensemble, iso_scores

def save_results(df, iso_anomaly, lof_anomaly, ensemble, iso_scores):
    df['iso_forest_anomaly'] = iso_anomaly
    df['lof_anomaly'] = lof_anomaly
    df['ensemble_anomaly'] = ensemble
    df['anomaly_score'] = -iso_scores

    engine = create_engine(DB_URL)
    raw = engine.raw_connection().connection
    try:
        cur = raw.cursor()
        cur.execute("DROP TABLE IF EXISTS anomalies_staging CASCADE")

        type_map = {np.dtype('int64'): 'BIGINT', np.dtype('float64'): 'DOUBLE PRECISION'}
        col_defs = ', '.join([f'"{c}" {type_map.get(df[c].dtype, "TEXT")}' for c in df.columns])
        cur.execute(f"CREATE TABLE anomalies_staging ({col_defs})")

        buf = io.StringIO()
        df.to_csv(buf, index=False, header=False)
        buf.seek(0)

        cur.copy_from(buf, 'anomalies_staging', sep=',', columns=df.columns.tolist())
        raw.commit()
        cur.close()
    finally:
        raw.close()

    print(f"Saved {len(df)} rows to anomalies_staging")
    print(f"Anomalies detected: {int(ensemble.sum())} ({ensemble.mean()*100:.1f}%)")

if __name__ == '__main__':
    df = load_data()
    features_scaled, numeric_cols = prepare_features(df)
    iso_anomaly, lof_anomaly, ensemble, iso_scores = detect_anomalies(features_scaled)
    save_results(df, iso_anomaly, lof_anomaly, ensemble, iso_scores)
