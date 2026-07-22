import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import text
from db import engine
from queries import *
from config import CRIT_COLORS
from components import kpi_card, fmt_currency, fmt_pct, verdict_badge, export_button

st.markdown("### Профиль компании")

with engine.connect() as conn:
    companies = conn.execute(text(Q_ALL_COMPANIES)).fetchall()
opts = {f"{c.company_id} — {c.company_name}": c.company_id for c in companies}

idx = 0
if "selected_company" in st.session_state:
    for i, (l, cid) in enumerate(opts.items()):
        if cid == st.session_state["selected_company"]:
            idx = i
            break
    del st.session_state["selected_company"]

sel = st.selectbox("Компания", list(opts.keys()), index=idx)
cid = opts[sel]

with engine.connect() as conn:
    tl = pd.read_sql(text(Q_COMPANY_TIMELINE), conn, params={"cid": cid})
    an = pd.read_sql(text(Q_COMPANY_ANOMALIES), conn, params={"cid": cid})
    fl = pd.read_sql(text(Q_COMPANY_FLAGS), conn, params={"cid": cid})

if tl.empty:
    st.warning("Нет данных")
    st.stop()


last = tl.iloc[-1]
st.markdown(f"#### {sel}")

c1, c2, c3, c4 = st.columns(4)
with c1: st.markdown(kpi_card("Выручка", fmt_currency(last["revenue"]), "#4DA6FF"), unsafe_allow_html=True)
with c2: st.markdown(kpi_card("Прибыль", fmt_currency(last["net_profit"]), "#2ed573" if last["net_profit"] and last["net_profit"] > 0 else "#ff4b4b"), unsafe_allow_html=True)
with c3: st.markdown(kpi_card("Маржа", fmt_pct(last["net_margin"]), "#feca57"), unsafe_allow_html=True)
with c4: st.markdown(kpi_card("Штат", str(int(last["headcount"])) if last["headcount"] else "—"), unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)
with c1: st.markdown(kpi_card("tax_to_profit", fmt_pct(last["tax_to_profit"]), "#4DA6FF"), unsafe_allow_html=True)
with c2: st.markdown(kpi_card("FPR", f"{last['fpr']:.2f}" if last["fpr"] else "—"), "#ff9f43"), unsafe_allow_html=True)
with c3: st.markdown(kpi_card("Аномалий", str(int(last["anomaly_count"]))), "#FFF"), unsafe_allow_html=True)
with c4:
    badge = verdict_badge(last)
    clr = "#ff4b4b" if "КРИТИЧЕСКИЙ" in badge else "#ff9f43" if "ВЫСОКИЙ" in badge else "#2ed573"
    st.markdown(kpi_card("Статус", badge.split("—")[0].strip(), clr), unsafe_allow_html=True)

st.markdown(f'<div style="padding:8px;background:#333;border-radius:8px;color:#FFF;margin-bottom:16px">{badge}</div>', unsafe_allow_html=True)

c1, c2 = st.columns(2)
with c1:
    fig = go.Figure()
    fig.add_trace(go.Bar(x=tl["year"], y=tl["revenue"] / 1_000_000, name="Выручка (млн)", marker_color="#4DA6FF"))
    fig.add_trace(go.Scatter(x=tl["year"], y=tl["net_profit"] / 1_000_000, name="Прибыль (млн)", mode="lines+markers", line=dict(color="#2ed573", width=3)))
    fig.update_layout(title="Выручка и прибыль")
    st.plotly_chart(fig, use_container_width=True)
with c2:
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=tl["year"], y=tl["net_margin"] * 100, name="Маржа %", mode="lines+markers", line=dict(color="#4DA6FF", width=3)))
    fig.add_trace(go.Scatter(x=tl["year"], y=tl["tax_to_profit"], name="tax_to_profit", mode="lines+markers", line=dict(color="#ff9f43", width=2), yaxis="y2"))
    fig.update_layout(title="Маржа и налоги", yaxis2=dict(overlaying="y", side="right"))
    st.plotly_chart(fig, use_container_width=True)

fig = go.Figure()
fig.add_trace(go.Bar(x=tl["year"], y=tl["headcount"], name="Штат", marker_color="#feca57"))
if tl["revenue"].sum() > 0:
    fig.add_trace(go.Scatter(x=tl["year"], y=tl["revenue"] / tl["headcount"].clip(lower=1), name="Выручка/сотр", mode="lines+markers", line=dict(color="#4DA6FF", width=2), yaxis="y2"))
    fig.update_layout(yaxis2=dict(overlaying="y", side="right"))
fig.update_layout(title="Штат и производительность")
st.plotly_chart(fig, use_container_width=True)

if not an.empty:
    st.markdown("#### Аномалии компании")
    st.dataframe(an.style.apply(lambda r: [f"background:{CRIT_COLORS.get(r['criticality'],'')};color:#FFF" if r['criticality'] in CRIT_COLORS else "" for _ in r.index], axis=1), use_container_width=True, hide_index=True)
    export_button(an, f"{cid}_anomalies.csv")

if not fl.empty:
    st.markdown("#### Флаги H1–H6")
    hm = fl.set_index("year")[[f"h{i}_flag" for i in range(1, 7)]]
    hm.columns = [f"H{i}" for i in range(1, 7)]
    st.plotly_chart(px.imshow(hm.T, text_auto=True, aspect="auto", color_continuous_scale="RdYlGn"), use_container_width=True)
