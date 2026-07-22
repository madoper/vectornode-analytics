import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import text
from db import engine
from queries import Q_GROUPS
from config import CRIT_COLORS
from components import export_button

st.markdown("### Групповой анализ")

gtype = st.radio("Тип группы", ["founder", "address"], horizontal=True)

with engine.connect() as conn:
    grp = pd.read_sql(text(Q_GROUPS), conn, params={"gtype": gtype})

if grp.empty:
    st.info("Нет данных")
    st.stop()

st.markdown(f"#### Всего групп: {len(grp)}")
st.dataframe(grp.style.apply(lambda r: [f"background:{CRIT_COLORS.get(r['criticality_final'],'')};color:#FFF" if r['criticality_final'] in CRIT_COLORS else "" for _ in r.index], axis=1), use_container_width=True, hide_index=True)
export_button(grp, f"groups_{gtype}.csv")

top = grp.nlargest(20, "anomaly_count")
fig = px.bar(top, x="anomaly_count", y="group_key", orientation="h",
              color="max_criticality_score", color_continuous_scale="Reds",
              labels={"anomaly_count": "Аномалий", "group_key": "Группа"},
              title=f"Топ-20 ({gtype})")
fig.update_layout(yaxis_categoryorder="total ascending")
st.plotly_chart(fig, use_container_width=True)

sel = st.selectbox("Детализация", grp["group_key"])
det = grp[grp["group_key"] == sel]
if not det.empty:
    st.dataframe(det, use_container_width=True, hide_index=True)
