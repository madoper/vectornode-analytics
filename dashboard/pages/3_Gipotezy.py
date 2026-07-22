import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import text
from db import engine
from queries import *
from config import CRIT_COLORS, HYPOTHESIS_LABELS
from components import fmt_z, export_button

st.set_page_config(page_title="ФНС Аналитика — Гипотезы", page_icon="logo.svg", layout="wide")
st.title("🧪 Анализ гипотез")

# ── Summary table ──
with engine.connect() as conn:
    hs = pd.read_sql(text(Q_HYPOTHESIS_SUMMARY), conn)
st.markdown("### Сводка по гипотезам")
styled = hs.style.apply(lambda r: [f"background:{CRIT_COLORS.get(r['criticality'],'#333')};color:#FFF" if r['criticality'] in CRIT_COLORS else "" for _ in r.index], axis=1)
st.dataframe(styled, use_container_width=True, hide_index=True)
export_button(hs, "hypothesis_summary.csv")

# ── Filters ──
hyps = sorted(hs["hypothesis_code"].unique())
h = st.selectbox("Гипотеза", hyps, format_func=lambda x: HYPOTHESIS_LABELS.get(x, x))

with engine.connect() as conn:
    years_raw = conn.execute(text(Q_HYPOTHESIS_YEARS)).fetchall()
year_opts = ["Все"] + [str(y[0]) for y in years_raw]
y = st.selectbox("Год", year_opts)

# ── Scatter plot ──
with engine.connect() as conn:
    scatter = pd.read_sql(text(Q_ANOMALY_SCATTER), conn, params={"h": h, "y": None if y == "Все" else int(y)})

st.markdown(f"### Scatter: z-score vs value — {HYPOTHESIS_LABELS.get(h, h)}")
if not scatter.empty:
    scatter_plot = scatter.dropna(subset=["zscore"]).copy()
    if not scatter_plot.empty:
        fig = px.scatter(scatter_plot, x="value", y="zscore", color="criticality",
                         size=scatter_plot["net_profit"].abs().clip(upper=scatter_plot["net_profit"].abs().quantile(0.95)),
                         hover_data=["company_name", "year", "interpretation"],
                         color_discrete_map=CRIT_COLORS,
                         labels={"value": "Значение", "zscore": "Z-score"})
        fig.add_hline(y=2, line_dash="dash", line_color="#feca57", annotation_text="z=+2")
        fig.add_hline(y=-2, line_dash="dash", line_color="#feca57", annotation_text="z=-2")
        fig.add_hline(y=3, line_dash="dash", line_color="#ff4b4b", annotation_text="z=+3")
        fig.add_hline(y=-3, line_dash="dash", line_color="#ff4b4b", annotation_text="z=-3")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Нет данных с z-score")
else:
    st.info("Нет данных")

# ── Company table ──
st.markdown("### Компании по гипотезе")
if not scatter.empty:
    display = scatter.sort_values("zscore", key=lambda x: x.abs(), ascending=False)
    st.dataframe(display, use_container_width=True, hide_index=True)
    export_button(display, f"{h}_companies.csv")

    # Click to navigate
    if st.button("🔍 Перейти к компании", key="goto_company"):
        top = display.iloc[0]
        st.session_state["selected_company"] = top["company_id"]
        st.switch_page("pages/2_Kompania.py")
