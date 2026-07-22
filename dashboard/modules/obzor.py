import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import text
from db import engine
from queries import *
from config import RESUME_TEXT, KEY_COMPANIES, CRIT_COLORS
from components import kpi_card, export_button

st.title("Обзор")

with engine.connect() as conn:
    kpi = conn.execute(text(Q_KPI)).fetchone()

col1, col2, col3, col4 = st.columns(4)
with col1: st.markdown(kpi_card("Компаний в анализе", kpi[0], "#4DA6FF"), unsafe_allow_html=True)
with col2: st.markdown(kpi_card("Критических аномалий", kpi[1], "#ff4b4b"), unsafe_allow_html=True)
with col3: st.markdown(kpi_card("Risk-компаний", kpi[2], "#ff9f43"), unsafe_allow_html=True)
with col4: st.markdown(kpi_card("Период", kpi[3], "#2ed573"), unsafe_allow_html=True)

with st.expander("Итоговое резюме", expanded=True):
    st.markdown(RESUME_TEXT)
    st.markdown("#### Расшифровка ключевых маркеров")
    mk = pd.DataFrame(KEY_COMPANIES)
    st.dataframe(mk, column_config={
        "company_id": "ID", "name": "Компания", "marker": "Маркер",
        "basis": "Основание", "priority": "Приоритет",
    }, use_container_width=True, hide_index=True)
    export_button(mk, "key_companies.csv")

with engine.connect() as conn:
    h1 = conn.execute(text(Q_PRIORITY_H1)).fetchall()
    h5 = conn.execute(text(Q_PRIORITY_H5_TRANSIT)).fetchall()
    h4 = conn.execute(text(Q_PRIORITY_H4_LOSS)).fetchall()
    h3 = conn.execute(text(Q_PRIORITY_H3_LOW_MARGIN)).fetchall()
    good = conn.execute(text(Q_GOOD_COMPANIES)).fetchall()

def card(col, title, color, items, fields):
    with col:
        html = f'<div style="border:2px solid {color};border-radius:8px;padding:8px;height:380px;overflow-y:auto"><h5 style="color:{color}">{title}</h5>'
        for it in items:
            name = getattr(it, "company_name", "") or it[1]
            html += f"<b>{name}</b><br>"
            for i, f in enumerate(fields):
                v = getattr(it, f, None) or (it[i + 2] if len(it) > i + 2 else "")
                html += f"<small>{f}: {v}</small><br>"
            html += "<hr>"
        html += "</div>"
        st.markdown(html, unsafe_allow_html=True)

c1, c2, c3, c4, c5 = st.columns(5)
card(c1, "Вывод средств H1", "#ff4b4b", h1, ["dividends_paid", "net_profit"])
card(c2, "Транзит H5", "#ff9f43", h5, ["revenue", "zscore"])
card(c3, "Убытки+давление H4", "#feca57", h4, ["fpr", "net_profit"])
card(c4, "Низкая маржа H3", "#a855f7", h3, ["net_margin", "zscore"])
card(c5, "Добросовестные", "#2ed573", good, ["top_hypothesis_code", "top_reason"])

with engine.connect() as conn:
    hs = pd.read_sql(text(Q_HYPOTHESIS_SUMMARY), conn)

c1, c2 = st.columns(2)
with c1:
    st.plotly_chart(px.bar(hs, x="hypothesis_code", y="findings_count", color="criticality",
                            color_discrete_map=CRIT_COLORS, barmode="stack"), use_container_width=True)
with c2:
    st.plotly_chart(px.treemap(hs, path=["hypothesis_code"], values="findings_count",
                                color="criticality", color_discrete_map=CRIT_COLORS), use_container_width=True)

st.markdown("""**Рекомендации:**
1. Выездные проверки: C0254, C0069, C0008, C0288.
2. Сверка: C0473, C0385.
3. Пояснения: C0380, C0308.
4. Анализ групп founder_id на дробление.
""")
