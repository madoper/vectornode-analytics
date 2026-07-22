from __future__ import annotations

import sys, os, io
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from sqlalchemy import create_engine


DB_CONN_ID = "analytics_db"
CSV_PATH = "/opt/analytics/data/test_dataset.csv"

EXPECTED_COLUMNS = [
    "company_id", "company_name", "inn", "ogrn_year", "region",
    "okved_code", "okved_section", "founder_id", "address_hash", "year",
    "revenue", "cost_of_goods", "gross_profit", "opex",
    "operating_profit", "net_profit", "taxes_paid", "headcount",
    "payroll_fund", "dividends_paid",
]

METRICS_FOR_ZSCORE = [
    "net_margin", "rev_per_emp", "financial_pressure_ratio",
    "rev_growth", "emp_growth",
]

DEFAULT_THRESHOLDS = {
    "z_critical": 3.0,
    "z_high": 2.0,
    "payout_critical": 1.5,
    "payout_high": 1.0,
    "rev_growth_high": 0.15,
    "emp_growth_high": -0.05,
    "fin_pressure_critical": 2.0,
    "fin_pressure_high": 1.2,
    "multi_flags_critical": 2,
}


def get_engine():
    hook = PostgresHook(postgres_conn_id=DB_CONN_ID)
    return hook.get_sqlalchemy_engine()


def read_sql_df(query, engine):
    """Read SQL query into DataFrame using raw connection (avoids pandas 3.x incompatibility)."""
    fairy = engine.raw_connection()
    try:
        return pd.read_sql(query, fairy.connection)
    finally:
        fairy.close()


def df_to_sql_copy(df, table_name, engine, schema="analytics"):
    """Write DataFrame to PostgreSQL using psycopg2 COPY."""
    fairy = engine.raw_connection()
    conn = fairy.connection
    try:
        cur = conn.cursor()
        cur.execute(f"CREATE SCHEMA IF NOT EXISTS {schema}")
        cur.execute(f"DROP TABLE IF EXISTS {schema}.{table_name} CASCADE")

        type_map = {np.dtype('int64'): 'BIGINT', np.dtype('float64'): 'DOUBLE PRECISION', np.dtype('int32'): 'INTEGER', np.dtype('object'): 'TEXT'}
        col_defs = ', '.join([f'"{c}" {type_map.get(df[c].dtype, "TEXT")}' for c in df.columns])
        try:
            cur.execute(f"CREATE TABLE {schema}.{table_name} ({col_defs})")
        except Exception as e:
            raise RuntimeError(f"CREATE TABLE failed. cols={df.columns.tolist()!r}, dtypes={dict(df.dtypes)!r}, col_defs={col_defs!r}") from e

        buf = io.StringIO()
        df.to_csv(buf, index=False, header=True)
        buf.seek(0)
        cur.copy_expert(f"COPY {schema}.{table_name} FROM STDIN WITH CSV HEADER", buf)
        conn.commit()
        cur.close()
    finally:
        fairy.close()


def validate_dataset(df: pd.DataFrame) -> None:
    missing = set(EXPECTED_COLUMNS) - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns: {missing}")

    df["year"] = pd.to_numeric(df["year"], errors="coerce")
    years = set(df["year"].dropna().unique())
    expected_years = {2023, 2024, 2025}
    if years != expected_years:
        raise ValueError(f"Invalid years: {years}. Expected {expected_years}")

    duplicates = df.duplicated(subset=["company_id", "year"]).sum()
    if duplicates:
        raise ValueError(f"Found duplicates company_id+year: {duplicates}")

    companies = df["company_id"].nunique()
    rows = len(df)
    if companies < 10:
        raise ValueError(f"Expected at least 10 companies, got {companies}")
    if rows != companies * 3:
        raise ValueError(f"Expected {companies*3} rows (3 per company), got {rows}")


def load_raw(**context):
    import time
    start = time.time()

    df = pd.read_csv(CSV_PATH)
    validate_dataset(df)
    df = df.sort_values(["company_id", "year"]).reset_index(drop=True)

    engine = get_engine()

    df_to_sql_copy(df, "test_dataset", engine, schema="staging")

    companies = df[["company_id", "company_name", "inn", "ogrn_year", "region",
                     "okved_code", "okved_section", "founder_id", "address_hash"]].drop_duplicates("company_id")
    df_to_sql_copy(companies, "company", engine, schema="analytics")

    year_cols = ["company_id", "year", "revenue", "cost_of_goods", "gross_profit",
                  "opex", "operating_profit", "net_profit", "taxes_paid",
                  "headcount", "payroll_fund", "dividends_paid"]
    df_to_sql_copy(df[year_cols], "company_year", engine, schema="analytics")

    elapsed = time.time() - start
    return {
        "elapsed_sec": round(elapsed, 2),
        "rows": int(len(df)),
        "companies": int(df["company_id"].nunique()),
        "years": sorted(df["year"].unique().tolist()),
    }


def build_features(**context):
    import time
    start = time.time()
    engine = get_engine()

    df = read_sql_df("SELECT * FROM staging.test_dataset", engine)
    df = df.sort_values(["company_id", "year"]).reset_index(drop=True)

    numeric_cols = [
        "revenue", "cost_of_goods", "gross_profit", "opex",
        "operating_profit", "net_profit", "taxes_paid",
        "headcount", "payroll_fund", "dividends_paid",
    ]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Derived features
    df["net_margin"] = df["net_profit"] / df["revenue"].replace(0, np.nan)
    df["gross_margin"] = df["gross_profit"] / df["revenue"].replace(0, np.nan)
    df["operating_margin"] = df["operating_profit"] / df["revenue"].replace(0, np.nan)
    df["rev_per_emp"] = df["revenue"] / df["headcount"].replace(0, np.nan)
    df["profit_per_emp"] = df["net_profit"] / df["headcount"].replace(0, np.nan)
    df["payroll_per_emp"] = df["payroll_fund"] / df["headcount"].replace(0, np.nan)
    df["tax_to_profit"] = np.where(
        df["net_profit"] > 0,
        df["taxes_paid"] / df["net_profit"],
        np.nan,
    )
    df["payout_ratio"] = np.where(
        df["net_profit"] > 0,
        df["dividends_paid"] / df["net_profit"],
        np.nan,
    )
    df["financial_pressure_ratio"] = (
        df["opex"] + df["taxes_paid"] + df["dividends_paid"]
    ) / df["gross_profit"].replace(0, np.nan)
    df["company_age"] = df["year"] - df["ogrn_year"]

    # Growth rates
    grouped = df.groupby("company_id")
    df["rev_growth"] = grouped["revenue"].pct_change()
    df["profit_growth"] = grouped["net_profit"].pct_change()
    df["emp_growth"] = grouped["headcount"].pct_change()
    df["payroll_growth"] = grouped["payroll_fund"].pct_change()

    # Classify profit growth direction
    df["profit_growth_type"] = "normal"
    prev_profit = df.groupby("company_id")["net_profit"].shift(1)
    mask_turnaround = (prev_profit <= 0) & (df["net_profit"] > 0)
    mask_deterioration = (prev_profit > 0) & (df["net_profit"] <= 0)
    mask_loss_change = (prev_profit <= 0) & (df["net_profit"] <= 0)
    df.loc[mask_turnaround, "profit_growth_type"] = "turnaround"
    df.loc[mask_deterioration, "profit_growth_type"] = "deterioration"
    df.loc[mask_loss_change, "profit_growth_type"] = "loss_change"

    features = df[[
        "company_id", "year", "net_margin", "gross_margin", "operating_margin",
        "rev_per_emp", "profit_per_emp", "payroll_per_emp",
        "tax_to_profit", "payout_ratio", "financial_pressure_ratio", "company_age",
    ]]

    growth = df[[
        "company_id", "year", "rev_growth", "profit_growth", "emp_growth",
        "payroll_growth", "profit_growth_type",
    ]]

    df_to_sql_copy(features, "company_features", engine, schema="analytics")
    df_to_sql_copy(growth, "company_growth", engine, schema="analytics")

    elapsed = time.time() - start
    return {"elapsed_sec": round(elapsed, 2), "features_rows": int(len(features)), "growth_rows": int(len(growth))}


def robust_zscore_series(series: pd.Series) -> pd.Series:
    median = series.median()
    mad = (series - median).abs().median()
    if mad and mad > 0:
        return (series - median) / (1.4826 * mad)
    std = series.std()
    if std and std > 0:
        return (series - median) / std
    return pd.Series(0.0, index=series.index)


def build_zscore(**context):
    import time
    start = time.time()
    engine = get_engine()

    query = """
        SELECT f.company_id, f.year, c.okved_section,
               f.net_margin, f.rev_per_emp, f.financial_pressure_ratio,
               g.rev_growth, g.emp_growth
        FROM analytics.company_features f
        JOIN analytics.company c ON c.company_id = f.company_id
        LEFT JOIN analytics.company_growth g ON g.company_id = f.company_id AND g.year = f.year
    """
    df = read_sql_df(query, engine)
    records = []

    for metric in METRICS_FOR_ZSCORE:
        if metric not in df.columns:
            continue
        tmp = df[["company_id", "year", "okved_section", metric]].dropna(subset=[metric]).copy()
        if tmp.empty:
            continue
        tmp["zscore"] = tmp.groupby(["okved_section", "year"])[metric].transform(robust_zscore_series)
        tmp["metric"] = metric
        records.append(tmp[["company_id", "year", "metric", "zscore"]])

    if not records:
        raise ValueError("No zscore records calculated")

    zscore = pd.concat(records, ignore_index=True)

    df_to_sql_copy(zscore, "company_zscore", engine, schema="analytics")

    elapsed = time.time() - start
    return {"elapsed_sec": round(elapsed, 2), "zscore_rows": int(len(zscore))}


def detect_anomalies(**context):
    import time
    start = time.time()
    engine = get_engine()
    th = DEFAULT_THRESHOLDS

    query = """
        SELECT c.company_id, c.company_name, c.okved_section, c.region,
               c.founder_id, c.address_hash, cy.year,
               cy.revenue, cy.net_profit, cy.gross_profit, cy.opex,
               cy.taxes_paid, cy.dividends_paid, cy.headcount,
               cf.net_margin, cf.payout_ratio, cf.financial_pressure_ratio, cf.rev_per_emp,
               g.rev_growth, g.emp_growth, g.profit_growth,
               z1.zscore AS net_margin_zscore,
               z2.zscore AS rev_per_emp_zscore,
               z3.zscore AS financial_pressure_zscore,
               z4.zscore AS rev_growth_zscore,
               z5.zscore AS emp_growth_zscore
        FROM analytics.company c
        JOIN analytics.company_year cy ON cy.company_id = c.company_id
        LEFT JOIN analytics.company_features cf ON cf.company_id = cy.company_id AND cf.year = cy.year
        LEFT JOIN analytics.company_growth g ON g.company_id = cy.company_id AND g.year = cy.year
        LEFT JOIN analytics.company_zscore z1 ON z1.company_id = cy.company_id AND z1.year = cy.year AND z1.metric = 'net_margin'
        LEFT JOIN analytics.company_zscore z2 ON z2.company_id = cy.company_id AND z2.year = cy.year AND z2.metric = 'rev_per_emp'
        LEFT JOIN analytics.company_zscore z3 ON z3.company_id = cy.company_id AND z3.year = cy.year AND z3.metric = 'financial_pressure_ratio'
        LEFT JOIN analytics.company_zscore z4 ON z4.company_id = cy.company_id AND z4.year = cy.year AND z4.metric = 'rev_growth'
        LEFT JOIN analytics.company_zscore z5 ON z5.company_id = cy.company_id AND z5.year = cy.year AND z5.metric = 'emp_growth'
    """
    df = read_sql_df(query, engine)
    anomalies = []

    def add_a(row, code, metric, value, zscore, interp, reason, crit, score):
        anomalies.append({
            "company_id": row["company_id"],
            "year": int(row["year"]),
            "hypothesis_code": code,
            "metric": metric or "",
            "value": float(value) if pd.notna(value) else None,
            "zscore": float(zscore) if pd.notna(zscore) else None,
            "interpretation": interp,
            "interpretation_reason": reason,
            "criticality": crit,
            "criticality_score": score,
        })

    for _, row in df.iterrows():
        flags = 0
        risk_flags = 0

        # H1 - dividend policy
        if pd.notna(row["dividends_paid"]) and row["dividends_paid"] > 0:
            if pd.notna(row["net_profit"]) and row["net_profit"] <= 0:
                flags += 1; risk_flags += 1
                add_a(row, "H1", "dividends_paid", row["dividends_paid"], None,
                      "risk", "Дивиденды выплачены при убытке. Агрессивная дивидендная политика или вывод средств.", "critical", 4)
            elif pd.notna(row["payout_ratio"]) and row["payout_ratio"] >= th["payout_critical"]:
                flags += 1; risk_flags += 1
                add_a(row, "H1", "payout_ratio", row["payout_ratio"], None,
                      "risk", f"payout_ratio >= {th['payout_critical']}. Агрессивная дивидендная политика.", "critical", 4)
            elif pd.notna(row["payout_ratio"]) and row["payout_ratio"] >= th["payout_high"]:
                flags += 1; risk_flags += 1
                add_a(row, "H1", "payout_ratio", row["payout_ratio"], None,
                      "risk", f"payout_ratio >= {th['payout_high']}. Повышенная дивидендная нагрузка.", "high", 3)

        # H2 - revenue growth + headcount reduction
        if pd.notna(row["rev_growth"]) and pd.notna(row["emp_growth"]) \
                and row["rev_growth"] >= th["rev_growth_high"] and row["emp_growth"] <= th["emp_growth_high"]:
            flags += 1
            if pd.notna(row["rev_per_emp_zscore"]) and row["rev_per_emp_zscore"] >= th["z_high"]:
                add_a(row, "H2", "rev_growth", row["rev_growth"], row["rev_per_emp_zscore"],
                      "economic_signal", "Рост выручки при сокращении штата с ростом rev_per_emp. Автоматизация/аутсорсинг.", "medium", 2)
            else:
                risk_flags += 1
                add_a(row, "H2", "rev_growth", row["rev_growth"], row["rev_per_emp_zscore"],
                      "risk", "Рост выручки при сокращении штата без роста производительности.", "high", 3)

        # H3 - margin outliers (sign-aware)
        if pd.notna(row["net_margin_zscore"]):
            z = row["net_margin_zscore"]
            if z >= th["z_critical"]:
                flags += 1
                add_a(row, "H3", "net_margin", row["net_margin"], z,
                      "economic_signal", "Маржа существенно выше отрасли. Высокая эффективность или ценовое преимущество.", "medium", 2)
            elif z <= -th["z_critical"]:
                flags += 1; risk_flags += 1
                add_a(row, "H3", "net_margin", row["net_margin"], z,
                      "risk", "Маржа существенно ниже отрасли. Аномалия учёта, демпинг или скрытые расходы.", "critical", 4)
            elif z >= th["z_high"]:
                flags += 1
                add_a(row, "H3", "net_margin", row["net_margin"], z,
                      "economic_signal", "Маржа выше отрасли. Повышенная эффективность.", "low", 1)
            elif z <= -th["z_high"]:
                flags += 1; risk_flags += 1
                add_a(row, "H3", "net_margin", row["net_margin"], z,
                      "risk", "Маржа ниже отрасли. Возможны операционные проблемы.", "high", 3)

        # H4 - financial pressure
        if pd.notna(row["financial_pressure_ratio"]):
            fpr = row["financial_pressure_ratio"]
            if fpr >= th["fin_pressure_critical"]:
                flags += 1; risk_flags += 1
                add_a(row, "H4", "financial_pressure_ratio", fpr, row.get("financial_pressure_zscore"),
                      "risk", "Высокое финансовое давление: opex+налоги+дивиденды слабо покрываются валовой прибылью.", "critical", 4)
            elif fpr >= th["fin_pressure_high"]:
                flags += 1; risk_flags += 1
                add_a(row, "H4", "financial_pressure_ratio", fpr, row.get("financial_pressure_zscore"),
                      "risk", "Повышенное финансовое давление по прокси-индикатору.", "high", 3)

        # H5 - rev_per_emp outlier (sign-aware)
        if pd.notna(row["rev_per_emp_zscore"]):
            z = row["rev_per_emp_zscore"]
            if z >= th["z_critical"]:
                flags += 1
                crit = "critical" if pd.notna(row["headcount"]) and row["headcount"] <= 5 else "high"
                add_a(row, "H5", "rev_per_emp", row["rev_per_emp"], z,
                      "economic_signal",
                      "Выручка на сотрудника выше отрасли. Автоматизация, крупный контракт или транзитные операции.", "high", 3)
            elif z <= -th["z_critical"]:
                flags += 1; risk_flags += 1
                add_a(row, "H5", "rev_per_emp", row["rev_per_emp"], z,
                      "risk",
                      "Выручка на сотрудника ниже отрасли. Возможна низкая производительность или избыточный штат.", "critical", 4)

        # H6 - multi-flag
        if flags >= th["multi_flags_critical"]:
            if risk_flags >= 2:
                add_a(row, "H6", "multi_flags", float(flags), None,
                      "risk", f"Сработало {flags} флагов (рисковых: {risk_flags}). Многомерная аномалия.", "critical", 4)
            else:
                add_a(row, "H6", "multi_flags", float(flags), None,
                      "economic_signal", f"Сработало {flags} флагов, большинство экономически объяснимо.", "medium", 2)

    a_df = pd.DataFrame(anomalies)
    if a_df.empty:
        a_df = pd.DataFrame(columns=["company_id", "year", "hypothesis_code", "metric",
                                       "value", "zscore", "interpretation", "interpretation_reason",
                                       "criticality", "criticality_score"])

    df_to_sql_copy(a_df, "anomaly", engine, schema="analytics")

    elapsed = time.time() - start
    return {"elapsed_sec": round(elapsed, 2), "anomaly_rows": int(len(a_df))}


def build_group_signals(**context):
    import time
    start = time.time()
    engine = get_engine()

    query = """
        SELECT c.founder_id, c.address_hash, a.company_id, a.year,
               a.criticality_score, a.interpretation
        FROM analytics.anomaly a
        JOIN analytics.company c ON c.company_id = a.company_id
    """
    df = read_sql_df(query, engine)

    if df.empty:
        return {"group_signal_rows": 0}

    founder = df.dropna(subset=["founder_id"]).groupby("founder_id").agg(
        companies_count=("company_id", "nunique"),
        risk_companies_count=("interpretation", lambda x: (x == "risk").sum()),
        avg_criticality_score=("criticality_score", "mean"),
        max_criticality_score=("criticality_score", "max"),
    ).reset_index()
    founder["group_type"] = "founder"
    founder = founder.rename(columns={"founder_id": "group_key"})

    address = df.dropna(subset=["address_hash"]).groupby("address_hash").agg(
        companies_count=("company_id", "nunique"),
        risk_companies_count=("interpretation", lambda x: (x == "risk").sum()),
        avg_criticality_score=("criticality_score", "mean"),
        max_criticality_score=("criticality_score", "max"),
    ).reset_index()
    address["group_type"] = "address"
    address = address.rename(columns={"address_hash": "group_key"})

    groups = pd.concat([founder, address], ignore_index=True)

    groups["interpretation"] = np.where(
        (groups["companies_count"] >= 3) & (groups["risk_companies_count"] >= 2),
        "risk", "neutral",
    )
    groups["interpretation_reason"] = np.where(
        groups["interpretation"] == "risk",
        "Связанная группа содержит несколько компаний с рисковыми сигналами.",
        "Группа не демонстрирует устойчивого рискового паттерна.",
    )

    cols = ["group_type", "group_key", "companies_count", "risk_companies_count",
            "avg_criticality_score", "max_criticality_score", "interpretation", "interpretation_reason"]
    groups = groups[cols]

    df_to_sql_copy(groups, "group_signal", engine, schema="analytics")

    # Create dashboard table (DISTINCT ON company+year to avoid LEFT JOIN duplicates)
    table_sql = """
    DROP TABLE IF EXISTS analytics.v_company_dashboard CASCADE;
    CREATE TABLE analytics.v_company_dashboard AS
    SELECT
        c.company_id, c.company_name, c.inn, c.ogrn_year, c.region,
        c.okved_code, c.okved_section, c.founder_id, c.address_hash,
        cy.year, cy.revenue, cy.cost_of_goods, cy.gross_profit, cy.opex,
        cy.operating_profit, cy.net_profit, cy.taxes_paid, cy.headcount,
        cy.payroll_fund, cy.dividends_paid,
        cf.net_margin, cf.gross_margin, cf.operating_margin,
        cf.rev_per_emp, cf.profit_per_emp, cf.payroll_per_emp,
        cf.tax_to_profit, cf.payout_ratio, cf.financial_pressure_ratio,
        cf.company_age,
        cg.rev_growth, cg.profit_growth, cg.emp_growth, cg.payroll_growth,
        z_net_margin.zscore     AS net_margin_zscore,
        z_rev_per_emp.zscore    AS rev_per_emp_zscore,
        z_fin_pressure.zscore   AS financial_pressure_zscore,
        z_rev_growth.zscore     AS rev_growth_zscore,
        z_emp_growth.zscore     AS emp_growth_zscore,
        a.hypothesis_code, a.metric, a.value,
        a.zscore AS anomaly_zscore,
        a.interpretation, a.interpretation_reason,
        a.criticality, a.criticality_score
    FROM analytics.company c
    JOIN analytics.company_year cy
      ON cy.company_id = c.company_id
    LEFT JOIN analytics.company_features cf
      ON cf.company_id = cy.company_id AND cf.year = cy.year
    LEFT JOIN analytics.company_growth cg
      ON cg.company_id = cy.company_id AND cg.year = cy.year
    LEFT JOIN analytics.company_zscore z_net_margin
      ON z_net_margin.company_id = cy.company_id AND z_net_margin.year = cy.year
     AND z_net_margin.metric = 'net_margin'
    LEFT JOIN analytics.company_zscore z_rev_per_emp
      ON z_rev_per_emp.company_id = cy.company_id AND z_rev_per_emp.year = cy.year
     AND z_rev_per_emp.metric = 'rev_per_emp'
    LEFT JOIN analytics.company_zscore z_fin_pressure
      ON z_fin_pressure.company_id = cy.company_id AND z_fin_pressure.year = cy.year
     AND z_fin_pressure.metric = 'financial_pressure_ratio'
    LEFT JOIN analytics.company_zscore z_rev_growth
      ON z_rev_growth.company_id = cy.company_id AND z_rev_growth.year = cy.year
     AND z_rev_growth.metric = 'rev_growth'
    LEFT JOIN analytics.company_zscore z_emp_growth
      ON z_emp_growth.company_id = cy.company_id AND z_emp_growth.year = cy.year
     AND z_emp_growth.metric = 'emp_growth'
    LEFT JOIN LATERAL (
        SELECT a2.hypothesis_code, a2.metric, a2.value, a2.zscore,
               a2.interpretation, a2.interpretation_reason,
               a2.criticality, a2.criticality_score
        FROM analytics.anomaly a2
        WHERE a2.company_id = c.company_id AND a2.year = cy.year
        ORDER BY a2.criticality_score DESC, a2.hypothesis_code
        LIMIT 1
    ) a ON true
    """
    fairy = engine.raw_connection()
    try:
        cursor = fairy.connection.cursor()
        cursor.execute(table_sql)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_v_dash_company ON analytics.v_company_dashboard(company_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_v_dash_year ON analytics.v_company_dashboard(year)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_v_dash_criticality ON analytics.v_company_dashboard(criticality)")
        fairy.connection.commit()
        cursor.close()
    finally:
        fairy.close()

    elapsed = time.time() - start
    return {"elapsed_sec": round(elapsed, 2), "group_signal_rows": int(len(groups))}


default_args = {
    "owner": "vectornode",
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="vectornode_anomaly_etl",
    default_args=default_args,
    description="ETL: CSV -> PostgreSQL -> features -> zscore -> anomalies -> Superset",
    schedule_interval=None,
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["vectornode", "analytics", "anomaly"],
) as dag:

    t_load_raw = PythonOperator(
        task_id="load_raw",
        python_callable=load_raw,
    )

    t_build_features = PythonOperator(
        task_id="build_features",
        python_callable=build_features,
    )

    t_build_zscore = PythonOperator(
        task_id="build_zscore",
        python_callable=build_zscore,
    )

    t_detect_anomalies = PythonOperator(
        task_id="detect_anomalies",
        python_callable=detect_anomalies,
    )

    t_build_group_signals = PythonOperator(
        task_id="build_group_signals",
        python_callable=build_group_signals,
    )

    t_load_raw >> t_build_features >> t_build_zscore >> t_detect_anomalies >> t_build_group_signals
