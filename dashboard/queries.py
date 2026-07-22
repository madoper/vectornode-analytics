Q_KPI = """
SELECT
    (SELECT COUNT(DISTINCT company_id) FROM reporting.rpt_company_year) AS total_companies,
    (SELECT COUNT(*) FROM reporting.rpt_anomaly WHERE criticality = 'critical') AS critical_anomalies,
    (SELECT COUNT(DISTINCT company_id) FROM reporting.rpt_company_year WHERE risk_flag = 1 AND is_latest_year = 1) AS risk_companies,
    (SELECT MIN(year) || '–' || MAX(year) FROM reporting.rpt_company_year) AS period;
"""

Q_HYPOTHESIS_SUMMARY = """
SELECT hypothesis_code, interpretation, criticality,
       findings_count, companies_count, company_year_count
FROM reporting.rpt_hypothesis_summary
ORDER BY hypothesis_code, criticality;
"""

Q_PRIORITY_H1 = """
SELECT DISTINCT a.company_id, a.company_name, a.year,
       a.dividends_paid, a.net_profit, a.zscore, a.criticality
FROM reporting.rpt_anomaly a
WHERE a.hypothesis_code = 'H1' AND a.criticality = 'critical'
ORDER BY a.year DESC, a.dividends_paid DESC;
"""

Q_PRIORITY_H5_TRANSIT = """
SELECT DISTINCT a.company_id, a.company_name, a.year,
       a.value AS revenue, a.headcount, a.zscore
FROM reporting.rpt_anomaly a
WHERE a.hypothesis_code = 'H5' AND a.zscore > 10
ORDER BY a.zscore DESC;
"""

Q_PRIORITY_H4_LOSS = """
SELECT DISTINCT a.company_id, a.company_name, a.year,
       a.financial_pressure_ratio AS fpr, a.net_profit
FROM reporting.rpt_anomaly a
WHERE a.hypothesis_code = 'H4' AND a.net_profit < 0
ORDER BY a.financial_pressure_ratio DESC;
"""

Q_PRIORITY_H3_LOW_MARGIN = """
SELECT DISTINCT a.company_id, a.company_name, a.year,
       a.value AS net_margin, a.zscore
FROM reporting.rpt_anomaly a
WHERE a.hypothesis_code = 'H3' AND a.zscore < -3
ORDER BY a.zscore ASC;
"""

Q_GOOD_COMPANIES = """
SELECT DISTINCT cy.company_id, cy.company_name, cy.year,
       cy.top_hypothesis_code, cy.top_reason
FROM reporting.rpt_company_year cy
WHERE cy.signal_only_flag = 1 AND cy.is_latest_year = 1
ORDER BY cy.company_name;
"""

Q_ALL_COMPANIES = """
SELECT DISTINCT company_id, company_name FROM reporting.rpt_company_year ORDER BY company_name;
"""

Q_COMPANY_TIMELINE = """
SELECT year, revenue, net_profit, dividends_paid, headcount,
       net_margin, tax_to_profit_valid AS tax_to_profit, financial_pressure_ratio AS fpr,
       rev_growth, emp_growth, anomaly_count, max_criticality_score,
       criticality_final, risk_flag, signal_only_flag
FROM reporting.rpt_company_year
WHERE company_id = %(cid)s
ORDER BY year;
"""

Q_COMPANY_ANOMALIES = """
SELECT year, hypothesis_code, metric, value, zscore,
       interpretation, interpretation_reason, criticality, criticality_score
FROM reporting.rpt_anomaly
WHERE company_id = %(cid)s
ORDER BY year, hypothesis_code;
"""

Q_COMPANY_FLAGS = """
SELECT year, h1_flag, h2_flag, h3_flag, h4_flag, h5_flag, h6_flag,
       h1_criticality, h2_criticality, h3_criticality,
       h4_criticality, h5_criticality, h6_criticality
FROM reporting.rpt_company_hypothesis_flags
WHERE company_id = %(cid)s
ORDER BY year;
"""

Q_ANOMALY_SCATTER = """
SELECT company_id, company_name, year, value, zscore,
       criticality, interpretation, net_profit, headcount
FROM reporting.rpt_anomaly
WHERE hypothesis_code = %(h)s AND (%(y)s IS NULL OR year = %(y)s)
ORDER BY ABS(zscore) DESC;
"""

Q_GROUPS = """
SELECT group_key, companies_count, risk_companies_count AS risk_anomaly_count,
       signal_companies_count AS signal_anomaly_count, anomaly_count,
       ROUND(avg_criticality_score::numeric, 2) AS avg_criticality_score,
       max_criticality_score, interpretation_final, criticality_final
FROM reporting.rpt_group_signal
WHERE group_type = %(gtype)s
ORDER BY max_criticality_score DESC, anomaly_count DESC;
"""

Q_HYPOTHESIS_YEARS = """
SELECT DISTINCT year FROM reporting.rpt_anomaly ORDER BY year;
"""

Q_INDUSTRY_MARGIN = """
SELECT okved_section, net_margin, company_name, company_id
FROM reporting.rpt_company_year
WHERE year = (SELECT MAX(year) FROM reporting.rpt_company_year)
  AND net_margin IS NOT NULL
ORDER BY okved_section;
"""

Q_INDUSTRY_TAX = """
SELECT okved_section,
       ROUND(AVG(tax_to_profit_valid)::numeric, 4) AS avg_tax_to_profit,
       ROUND(AVG(financial_pressure_ratio)::numeric, 4) AS avg_fpr
FROM reporting.rpt_company_year
WHERE is_latest_year = 1
GROUP BY okved_section
ORDER BY avg_fpr DESC;
"""
