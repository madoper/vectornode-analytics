import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import text
from db import engine
from queries import *
from config import CRIT_COLORS, HYPOTHESIS_LABELS
from components import kpi_card, fmt_currency, fmt_pct, fmt_z, verdict_badge, export_button

st.title("Профиль компании")

# ── Company selector ──
with engine.connect() as conn:
    companies = conn.execute(text(Q_ALL_COMPANIES)).fetchall()
comp_options = {f"{c.company_id} — {c.company_name}": c.company_id for c in companies}

# Read from session state if coming from overview
default_idx = 0
if "selected_company" in st.session_state:
    for i, (label, cid) in enumerate(comp_options.items()):
        if cid == st.session_state["selected_company"]:
            default_idx = i
            break
    del st.session_state["selected_company"]

sel_label = st.selectbox("Выберите компанию", list(comp_options.keys()), index=default_idx)
cid = comp_options[sel_label]

# ── Load data ──
with engine.connect() as conn:
    timeline = pd.read_sql(text(Q_COMPANY_TIMELINE), conn, params={"cid": cid})
    anomalies = pd.read_sql(text(Q_COMPANY_ANOMALIES), conn, params={"cid": cid})
    flags = pd.read_sql(text(Q_COMPANY_FLAGS), conn, params={"cid": cid})

if timeline.empty:
    st.warning("Нет данных")
    st.stop()

last = timeline.iloc[-1]

# ── KPI cards ──
st.markdown(f"### {sel_label}")
col1, col2, col3, col4 = st.columns(4)
with col1: st.markdown(kpi_card("Выручка", fmt_currency(last["revenue"]), "#4DA6FF"), unsafe_allow_html=True)
with col2: st.markdown(kpi_card("Чистая прибыль", fmt_currency(last["net_profit"]),
                                "#2ed573" if last["net_profit"] and last["net_profit"] > 0 else "#ff4b4b"), unsafe_allow_html=True)
with col3: st.markdown(kpi_card("Маржа", fmt_pct(last["net_margin"]), "#feca57"), unsafe_allow_html=True)
with col4: st.markdown(kpi_card("Штат", str(int(last["headcount"])) if last["headcount"] else "—"), unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)
with col1: st.markdown(kpi_card("tax_to_profit", fmt_pct(last["tax_to_profit"]), "#4DA6FF"), unsafe_allow_html=True)
with col2: st.markdown(kpi_card("FPR", f"{last['fpr']:.2f}" if last["fpr"] else "—", "#ff9f43"), unsafe_allow_html=True)
with col3: st.markdown(kpi_card("Аномалий", str(int(last["anomaly_count"]))), unsafe_allow_html=True)
with col4:
    badge = verdict_badge(last)
    color = "#ff4b4b" if "КРИТИЧЕСКИЙ" in badge else "#ff9f43" if "ВЫСОКИЙ" in badge else "#2ed573" if "ДОБРОСОВЕСТНЫЙ" in badge else "#57606f"
    st.markdown(kpi_card("Статус", badge.split("—")[0].strip(), color), unsafe_allow_html=True)

st.markdown(f'<div style="padding:8px;border-radius:8px;background:#333;color:#FFF;margin-bottom:16px">{badge}</div>', unsafe_allow_html=True)

# ── Timeline ──
col1, col2 = st.columns(2)
with col1:
    fig1 = go.Figure()
    fig1.add_trace(go.Bar(x=timeline["year"], y=timeline["revenue"] / 1_000_000, name="Выручка (млн)", marker_color="#4DA6FF"))
    fig1.add_trace(go.Scatter(x=timeline["year"], y=timeline["net_profit"] / 1_000_000, name="Чистая прибыль (млн)",
                               mode="lines+markers", line=dict(color="#2ed573", width=3)))
    fig1.update_layout(title="Выручка и прибыль")
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=timeline["year"], y=timeline["net_margin"] * 100, name="Маржа %",
                               mode="lines+markers", line=dict(color="#4DA6FF", width=3)))
    fig2.add_trace(go.Scatter(x=timeline["year"], y=timeline["tax_to_profit"], name="tax_to_profit",
                               mode="lines+markers", line=dict(color="#ff9f43", width=2), yaxis="y2"))
    fig2.update_layout(title="Маржа и налоговая нагрузка", yaxis2=dict(overlaying="y", side="right"))
    st.plotly_chart(fig2, use_container_width=True)

# Headcount chart
fig3 = go.Figure()
fig3.add_trace(go.Bar(x=timeline["year"], y=timeline["headcount"], name="Штат", marker_color="#feca57"))
if not timeline.empty and timeline["revenue"].sum() > 0:
    fig3.add_trace(go.Scatter(x=timeline["year"], y=timeline["revenue"] / timeline["headcount"].clip(lower=1),
                               name="Выручка/сотр", mode="lines+markers", line=dict(color="#4DA6FF", width=2), yaxis="y2"))
    fig3.update_layout(yaxis2=dict(overlaying="y", side="right"))
fig3.update_layout(title="Штат и производительность")
st.plotly_chart(fig3, use_container_width=True)

# ── Anomaly table ──
st.markdown("#### Аномалии компании")
if not anomalies.empty:
    styled = anomalies.style.apply(lambda r: [f"background:{CRIT_COLORS.get(r['criticality'],'#333')};color:#FFF" if r['criticality'] in CRIT_COLORS else "" for _ in r.index], axis=1)
    st.dataframe(styled, use_container_width=True, hide_index=True)
    export_button(anomalies, f"{cid}_anomalies.csv")
else:
    st.info("Нет аномалий")

# ── Flags heatmap ──
st.markdown("#### Флаги гипотез по годам")
if not flags.empty:
    heat = flags.set_index("year")[[f"h{i}_flag" for i in range(1, 7)]]
    heat.columns = [f"H{i}" for i in range(1, 7)]
    fig4 = px.imshow(heat.T, text_auto=True, aspect="auto", color_continuous_scale="RdYlGn",
                     labels={"x": "Год", "y": "Гипотеза", "color": "Флаг"})
    st.plotly_chart(fig4, use_container_width=True)
