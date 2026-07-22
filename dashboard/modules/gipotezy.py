import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import text
from db import engine
from queries import *
from config import CRIT_COLORS, HYPOTHESIS_LABELS
from components import export_button

st.title("Анализ гипотез")

with engine.connect() as conn:
    hs = pd.read_sql(text(Q_HYPOTHESIS_SUMMARY), conn)

st.markdown("#### Сводка")
st.dataframe(hs.style.apply(lambda r: [f"background:{CRIT_COLORS.get(r['criticality'],'')}" if r['criticality'] in CRIT_COLORS else "" for _ in r.index], axis=1), use_container_width=True, hide_index=True)
export_button(hs, "hypothesis_summary.csv")

hyps = sorted(hs["hypothesis_code"].unique())
h = st.selectbox("Гипотеза", hyps, format_func=lambda x: HYPOTHESIS_LABELS.get(x, x))

with engine.connect() as conn:
    yrs = [r[0] for r in conn.execute(text(Q_HYPOTHESIS_YEARS)).fetchall()]
y = st.selectbox("Год", ["Все"] + [str(y) for y in yrs])

with engine.connect() as conn:
    sc = pd.read_sql(text(Q_ANOMALY_SCATTER), conn, params={"h": h, "y": None if y == "Все" else int(y)})

sc_z = sc.dropna(subset=["zscore"]).copy()
if not sc_z.empty:
    fig = px.scatter(sc_z, x="value", y="zscore", color="criticality",
                     size=sc_z["net_profit"].abs().clip(upper=sc_z["net_profit"].abs().quantile(0.95)),
                     hover_data=["company_name", "year", "interpretation"],
                     color_discrete_map=CRIT_COLORS)
    fig.add_hline(y=2, line_dash="dash", line_color="#feca57")
    fig.add_hline(y=-2, line_dash="dash", line_color="#feca57")
    fig.add_hline(y=3, line_dash="dash", line_color="#ff4b4b")
    fig.add_hline(y=-3, line_dash="dash", line_color="#ff4b4b")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Нет данных с z-score")

st.markdown("#### Компании")
if not sc.empty:
    disp = sc.sort_values("zscore", key=lambda x: x.abs(), ascending=False)
    st.dataframe(disp, use_container_width=True, hide_index=True)
    if st.button("Перейти к компании"):
        st.session_state["selected_company"] = disp.iloc[0]["company_id"]
        st.rerun()
