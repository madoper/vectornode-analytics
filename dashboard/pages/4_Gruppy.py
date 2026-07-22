import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import text
from db import engine
from queries import Q_GROUPS
from config import CRIT_COLORS
from components import color_table, export_button

st.title("Групповой анализ")

gtype = st.radio("Тип группы", ["founder", "address"], horizontal=True)

with engine.connect() as conn:
    groups = pd.read_sql(text(Q_GROUPS), conn, params={"gtype": gtype})

st.markdown(f"### Все группы ({len(groups)})")
if not groups.empty:
    styled = groups.style.apply(lambda r: [f"background:{CRIT_COLORS.get(r['criticality_final'],'#333')};color:#FFF" if r['criticality_final'] in CRIT_COLORS else "" for _ in r.index], axis=1)
    st.dataframe(styled, use_container_width=True, hide_index=True)
    export_button(groups, f"groups_{gtype}.csv")

    # Top-20 bar chart
    top20 = groups.nlargest(20, "anomaly_count")
    fig = px.bar(top20, x="anomaly_count", y="group_key", orientation="h",
                  color="max_criticality_score", color_continuous_scale="Reds",
                  labels={"anomaly_count": "Аномалий", "group_key": "Группа"},
                  title=f"Топ-20 групп ({gtype})")
    fig.update_layout(yaxis_categoryorder="total ascending")
    st.plotly_chart(fig, use_container_width=True)

    # Group detail
    sel_group = st.selectbox("Детализация группы", groups["group_key"])
    detail = groups[groups["group_key"] == sel_group]
    if not detail.empty:
        st.dataframe(detail, use_container_width=True, hide_index=True)
        st.info("Детализация по компаниям группы требует JOIN по founder_id/address_hash (данные доступны в rpt_company_year)")
else:
    st.info("Нет данных")
