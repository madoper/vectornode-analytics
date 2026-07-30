__anchor__ = "analytics-router"

import asyncpg

from fastapi import APIRouter, HTTPException, Query

router = APIRouter(prefix="/api/v1/analytics", tags=["analytics"])

_pool: asyncpg.Pool | None = None


async def _get_pool() -> asyncpg.Pool:
    global _pool
    if _pool is None:
        from backend.shared.settings import settings
        _pool = await asyncpg.create_pool(
            host=settings.postgres_host,
            port=settings.postgres_port,
            user=settings.gateway_ro_user,
            password=settings.gateway_ro_password,
            database="analytics",
            min_size=1,
            max_size=3,
        )
    return _pool


@router.get("/company/{inn}")
async def company_card(inn: str):
    pool = await _get_pool()
    row = await pool.fetchrow("""
        SELECT company_id, company_name, inn, region, okved_section,
               revenue, net_profit, headcount, financial_pressure_ratio,
               net_margin, risk_flag, anomaly_count, criticality_final,
               h1_flag, h2_flag, h3_flag, h4_flag, h5_flag, h6_flag
        FROM reporting.rpt_company_year
        WHERE inn = $1 AND is_latest_year = 1
    """, inn)
    if not row:
        raise HTTPException(status_code=404, detail="Company not found")
    return dict(row)


@router.get("/companies/top")
async def top_risk(limit: int = Query(10, ge=1, le=50)):
    pool = await _get_pool()
    rows = await pool.fetch("""
        SELECT company_name, inn, max_criticality_score,
               anomaly_count, criticality_final
        FROM reporting.rpt_company_year
        WHERE risk_flag = 1 AND is_latest_year = 1
        ORDER BY max_criticality_score DESC
        LIMIT $1
    """, limit)
    return [dict(r) for r in rows]


@router.get("/company/{inn}/signals")
async def company_signals(inn: str):
    pool = await _get_pool()
    row = await pool.fetchrow("""
        SELECT h.h1_flag, h.h2_flag, h.h3_flag, h.h4_flag, h.h5_flag, h.h6_flag,
               h.h1_criticality, h.h2_criticality, h.h3_criticality,
               h.h4_criticality, h.h5_criticality, h.h6_criticality
        FROM reporting.rpt_company_hypothesis_flags h
        JOIN reporting.rpt_company_year cy ON cy.company_id = h.company_id AND cy.year = h.year
        WHERE cy.inn = $1 AND cy.is_latest_year = 1
    """, inn)
    if not row:
        raise HTTPException(status_code=404, detail="Company not found")
    return dict(row)


@router.get("/groups/top")
async def top_groups(limit: int = Query(5, ge=1, le=20)):
    pool = await _get_pool()
    rows = await pool.fetch("""
        SELECT group_key, companies_count, anomaly_count,
               criticality_final, interpretation_final
        FROM reporting.rpt_group_signal
        WHERE companies_count >= 2
        ORDER BY max_criticality_score DESC
        LIMIT $1
    """, limit)
    return [dict(r) for r in rows]


@router.get("/anomalies/recent")
async def recent_anomalies(days: int = Query(7, ge=1, le=90)):
    pool = await _get_pool()
    rows = await pool.fetch("""
        SELECT a.company_id, c.company_name, a.hypothesis_code,
               a.interpretation, a.criticality, a.detected_at
        FROM analytics.anomaly a
        JOIN analytics.company c USING (company_id)
        WHERE a.detected_at >= NOW() - INTERVAL '1 day' * $1
        ORDER BY a.detected_at DESC
        LIMIT 20
    """, days)
    return [dict(r) for r in rows]


@router.post("/companies/compare")
async def compare_companies(inn1: str, inn2: str):
    pool = await _get_pool()
    rows = await pool.fetch("""
        SELECT company_name, inn, revenue, net_profit, headcount,
               net_margin, financial_pressure_ratio, anomaly_count, criticality_final
        FROM reporting.rpt_company_year
        WHERE inn IN ($1, $2) AND is_latest_year = 1
    """, inn1, inn2)
    if len(rows) < 2:
        raise HTTPException(status_code=404, detail="One or both companies not found")
    return [dict(r) for r in rows]
