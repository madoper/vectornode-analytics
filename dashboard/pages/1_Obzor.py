import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import text
from db import engine
from queries import *
from config import RESUME_TEXT, KEY_COMPANIES, CRIT_COLORS, CRIT_ORDER
from components import kpi_card, fmt_currency, color_table, export_button

st.title("Обзор")

# ── KPI ──
with engine.connect() as conn:
    kpi = conn.execute(text(Q_KPI)).fetchone()

col1, col2, col3, col4 = st.columns(4)
with col1: st.markdown(kpi_card("Компаний в анализе", kpi[0], "#4DA6FF"), unsafe_allow_html=True)
with col2: st.markdown(kpi_card("Критических аномалий", kpi[1], "#ff4b4b"), unsafe_allow_html=True)
with col3: st.markdown(kpi_card("Risk-компаний", kpi[2], "#ff9f43"), unsafe_allow_html=True)
with col4: st.markdown(kpi_card("Период", kpi[3], "#2ed573"), unsafe_allow_html=True)

# ── Resume expander ──
with st.expander("Итоговое резюме", expanded=True):
    st.markdown(RESUME_TEXT)
    st.markdown("### Расшифровка ключевых маркеров")
    mk = pd.DataFrame(KEY_COMPANIES)
    st.dataframe(mk, column_config={
        "company_id": "ID", "name": "Компания", "marker": "Маркер",
        "basis": "Основание", "priority": "Приоритет",
    }, use_container_width=True, hide_index=True)
    export_button(mk, "key_companies.csv")

# ── 5 priority cards ──
with engine.connect() as conn:
    h1 = conn.execute(text(Q_PRIORITY_H1)).fetchall()
    h5 = conn.execute(text(Q_PRIORITY_H5_TRANSIT)).fetchall()
    h4 = conn.execute(text(Q_PRIORITY_H4_LOSS)).fetchall()
    h3 = conn.execute(text(Q_PRIORITY_H3_LOW_MARGIN)).fetchall()
    good = conn.execute(text(Q_GOOD_COMPANIES)).fetchall()

def render_card(col, title, color, items, fields):
    with col:
        html = f'<div style="border:2px solid {color};border-radius:8px;padding:8px;height:400px;overflow-y:auto">'
        html += f'<h5 style="color:{color};margin:0">{title}</h5>'
        for item in items:
            name = getattr(item, "company_name", "") or item[1]
            html += f"<b>{name}</b><br>"
            for i, f in enumerate(fields):
                val = getattr(item, f, None) or (item[i + 2] if len(item) > i + 2 else "")
                html += f"<small>{f}: {val}</small><br>"
            html += "<hr>"
        html += "</div>"
        st.markdown(html, unsafe_allow_html=True)

col1, col2, col3, col4, col5 = st.columns(5)
render_card(col1, "Вывод средств H1", "#ff4b4b", h1, ["dividends_paid", "net_profit"])
render_card(col2, "Транзит H5 (z>10)", "#ff9f43", h5, ["revenue", "zscore"])
render_card(col3, "Убытки+давление H4", "#feca57", h4, ["fpr", "net_profit"])
render_card(col4, "Низкая маржа H3", "#a855f7", h3, ["net_margin", "zscore"])
render_card(col5, "Добросовестные", "#2ed573", good, ["top_hypothesis_code", "top_reason"])

# ── Charts ──
with engine.connect() as conn:
    hs = pd.read_sql(text(Q_HYPOTHESIS_SUMMARY), conn)

col1, col2 = st.columns(2)
with col1:
    fig1 = px.bar(hs, x="hypothesis_code", y="findings_count", color="criticality",
                   color_discrete_map=CRIT_COLORS, barmode="stack",
                   title="Находки по гипотезам",
                   labels={"findings_count": "Находок", "hypothesis_code": "Гипотеза"})
    st.plotly_chart(fig1, use_container_width=True)
with col2:
    fig2 = px.treemap(hs, path=["hypothesis_code"], values="findings_count",
                       color="criticality", color_discrete_map=CRIT_COLORS,
                       title="Treemap гипотез")
    st.plotly_chart(fig2, use_container_width=True)

# ── Recommendations ──
st.markdown("### Рекомендации")
st.markdown("""
1. **Выездные проверки:** C0254, C0069, C0008, C0288 — признаки вывода средств, транзитные операции.
2. **Сверка:** C0473, C0385 — аномальная налоговая нагрузка (tax_to_profit 86 и 8,6).
3. **Пояснения:** C0380, C0308 — налоговая нагрузка ниже средней по отрасли.
4. **Анализ групп founder_id** на дробление бизнеса.
""")
