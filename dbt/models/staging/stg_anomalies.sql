with stg_anomalies as (
    select
        company_id,
        company_name,
        inn,
        ogrn_year,
        region,
        okved_code,
        okved_section,
        year,
        revenue,
        cost_of_goods,
        gross_profit,
        opex,
        operating_profit,
        net_profit,
        taxes_paid,
        headcount,
        payroll_fund,
        dividends_paid,
        iso_forest_anomaly,
        lof_anomaly,
        ensemble_anomaly,
        anomaly_score,
        CURRENT_TIMESTAMP as processed_at
    from public.anomalies_staging
)

select * from stg_anomalies
