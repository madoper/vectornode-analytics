with anomalies as (
    select * from {{ ref('stg_anomalies') }}
),

company_summary as (
    select
        company_id,
        company_name,
        inn,
        region,
        okved_section,
        count(*) as total_records,
        sum(ensemble_anomaly) as anomaly_count,
        round(avg(ensemble_anomaly) * 100::numeric, 2) as anomaly_pct,
        round(avg(anomaly_score)::numeric, 4) as avg_anomaly_score,
        round(avg(revenue)::numeric, 0) as avg_revenue,
        round(avg(net_profit)::numeric, 0) as avg_net_profit,
        round(avg(taxes_paid)::numeric, 0) as avg_taxes_paid,
        round(avg(headcount)::numeric, 0) as avg_headcount
    from anomalies
    group by 1, 2, 3, 4, 5
),

final as (
    select
        *,
        case
            when anomaly_pct >= 50 then 'Критический'
            when anomaly_pct >= 20 then 'Высокий'
            when anomaly_pct >= 5 then 'Средний'
            else 'Низкий'
        end as risk_level,
        CURRENT_TIMESTAMP as computed_at
    from company_summary
)

select * from final
