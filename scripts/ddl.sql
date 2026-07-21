-- VectorNode Analytics: DDL
-- Run: docker exec -i podft-postgres psql -U podft -d analytics < ddl.sql

-- Clean up old tables
DROP TABLE IF EXISTS anomalies_staging CASCADE;
DROP VIEW IF EXISTS public_staging.stg_anomalies CASCADE;
DROP TABLE IF EXISTS public_marts.company_risk_summary CASCADE;

-- Create schema
CREATE SCHEMA IF NOT EXISTS analytics;

-- Companies
CREATE TABLE IF NOT EXISTS analytics.company (
    company_id      TEXT PRIMARY KEY,
    company_name    TEXT,
    inn             TEXT,
    ogrn_year       INTEGER,
    region          TEXT,
    okved_code      TEXT,
    okved_section   TEXT,
    founder_id      TEXT,
    address_hash    TEXT
);

-- Financial data by year
CREATE TABLE IF NOT EXISTS analytics.company_year (
    company_id       TEXT NOT NULL REFERENCES analytics.company(company_id),
    year             INTEGER NOT NULL CHECK (year IN (2023, 2024, 2025)),
    revenue          NUMERIC(20, 2),
    cost_of_goods    NUMERIC(20, 2),
    gross_profit     NUMERIC(20, 2),
    opex             NUMERIC(20, 2),
    operating_profit NUMERIC(20, 2),
    net_profit       NUMERIC(20, 2),
    taxes_paid       NUMERIC(20, 2),
    headcount        INTEGER,
    payroll_fund     NUMERIC(20, 2),
    dividends_paid   NUMERIC(20, 2),
    PRIMARY KEY (company_id, year)
);

-- Derived features
CREATE TABLE IF NOT EXISTS analytics.company_features (
    company_id                TEXT NOT NULL,
    year                      INTEGER NOT NULL,
    net_margin                NUMERIC(20, 8),
    gross_margin              NUMERIC(20, 8),
    operating_margin          NUMERIC(20, 8),
    rev_per_emp               NUMERIC(20, 2),
    profit_per_emp            NUMERIC(20, 2),
    payroll_per_emp           NUMERIC(20, 2),
    tax_to_profit             NUMERIC(20, 8),
    payout_ratio              NUMERIC(20, 8),
    financial_pressure_ratio  NUMERIC(20, 8),
    company_age               INTEGER,
    PRIMARY KEY (company_id, year)
);

-- Growth rates
CREATE TABLE IF NOT EXISTS analytics.company_growth (
    company_id      TEXT NOT NULL,
    year            INTEGER NOT NULL,
    rev_growth      NUMERIC(20, 8),
    profit_growth   NUMERIC(20, 8),
    emp_growth      NUMERIC(20, 8),
    payroll_growth  NUMERIC(20, 8),
    PRIMARY KEY (company_id, year)
);

-- Z-scores
CREATE TABLE IF NOT EXISTS analytics.company_zscore (
    company_id TEXT NOT NULL,
    year       INTEGER NOT NULL,
    metric     TEXT NOT NULL,
    zscore     NUMERIC(20, 8),
    PRIMARY KEY (company_id, year, metric)
);

-- Anomalies (findings)
CREATE TABLE IF NOT EXISTS analytics.anomaly (
    anomaly_id            BIGSERIAL PRIMARY KEY,
    company_id            TEXT NOT NULL,
    year                  INTEGER NOT NULL,
    hypothesis_code       TEXT NOT NULL,
    metric                TEXT,
    value                 NUMERIC(20, 6),
    zscore                NUMERIC(20, 6),
    interpretation        TEXT NOT NULL,
    interpretation_reason TEXT,
    criticality           TEXT NOT NULL,
    criticality_score     INTEGER NOT NULL,
    detected_at           TIMESTAMP DEFAULT now()
);

-- Group signals
CREATE TABLE IF NOT EXISTS analytics.group_signal (
    group_signal_id       BIGSERIAL PRIMARY KEY,
    group_type            TEXT NOT NULL,
    group_key             TEXT NOT NULL,
    companies_count       INTEGER,
    risk_companies_count  INTEGER,
    avg_criticality_score NUMERIC(10, 4),
    max_criticality_score INTEGER,
    interpretation        TEXT,
    interpretation_reason TEXT,
    detected_at           TIMESTAMP DEFAULT now()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_anomaly_company
    ON analytics.anomaly(company_id, year);

CREATE INDEX IF NOT EXISTS idx_anomaly_hypothesis
    ON analytics.anomaly(hypothesis_code, criticality);

CREATE INDEX IF NOT EXISTS idx_group_signal_key
    ON analytics.group_signal(group_type, group_key);

-- Dashboard view
CREATE OR REPLACE VIEW analytics.v_company_dashboard AS
SELECT
    c.company_id,
    c.company_name,
    c.inn,
    c.ogrn_year,
    c.region,
    c.okved_code,
    c.okved_section,
    c.founder_id,
    c.address_hash,
    cy.year,
    cy.revenue,
    cy.cost_of_goods,
    cy.gross_profit,
    cy.opex,
    cy.operating_profit,
    cy.net_profit,
    cy.taxes_paid,
    cy.headcount,
    cy.payroll_fund,
    cy.dividends_paid,
    cf.net_margin,
    cf.gross_margin,
    cf.operating_margin,
    cf.rev_per_emp,
    cf.profit_per_emp,
    cf.payroll_per_emp,
    cf.tax_to_profit,
    cf.payout_ratio,
    cf.financial_pressure_ratio,
    cf.company_age,
    cg.rev_growth,
    cg.profit_growth,
    cg.emp_growth,
    cg.payroll_growth,
    z_net_margin.zscore     AS net_margin_zscore,
    z_rev_per_emp.zscore    AS rev_per_emp_zscore,
    z_fin_pressure.zscore   AS financial_pressure_zscore,
    z_rev_growth.zscore     AS rev_growth_zscore,
    z_emp_growth.zscore     AS emp_growth_zscore,
    a.hypothesis_code,
    a.metric,
    a.value,
    a.zscore AS anomaly_zscore,
    a.interpretation,
    a.interpretation_reason,
    a.criticality,
    a.criticality_score
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
LEFT JOIN analytics.anomaly a
  ON a.company_id = cy.company_id AND a.year = cy.year;
