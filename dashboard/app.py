import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="АНАЛИЗ РИСКОВ",
    page_icon="logo.svg",
    layout="wide",
    initial_sidebar_state="expanded",
)

from utils.data_loader import load_all
from utils.constants import (
    CRITICALITY_COLORS, CRITICALITY_ORDER, INTERPRETATION_COLORS,
    HYPOTHESIS_LABELS, HYPOTHESIS_METRICS,
)
from utils.charts import (
    format_rub, kpi_card, criticality_bar, hypothesis_bar,
    hypothesis_heatmap, scatter_zscore, line_chart, radar_zscores,
)

st.markdown("""
<style>
    .stApp { background-color: #0E1117; }
    .main h1, .main h2, .main h3 { color: #FFFFFF; }
    div[data-testid="stMetricValue"] { color: #FFFFFF !important; }

    header[data-testid="stHeader"] { visibility: hidden; height: 0; }

    section[data-testid="stSidebar"] div[data-testid="stMarkdownContainer"] p:last-child {
        display: none;
    }

    footer { visibility: hidden; }

    #custom-header {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        height: 56px;
        background-color: #0E1117;
        display: flex;
        align-items: center;
        padding: 0 16px;
        z-index: 9999;
        border-bottom: 1px solid #333;
    }
    #custom-header img {
        height: 40px;
        width: 40px;
    }
    #custom-header .title {
        position: absolute;
        left: 50%;
        transform: translateX(-50%);
        font-size: 20px;
        font-weight: 700;
        letter-spacing: 3px;
        color: #FFFFFF;
        white-space: nowrap;
    }

    div[data-testid="stTabs"] {
        position: sticky;
        top: 56px;
        z-index: 998;
        background-color: #0E1117;
        padding-top: 4px;
        padding-bottom: 4px;
        border-bottom: 1px solid #333;
    }
    div[data-testid="stTabs"] button {
        font-size: 14px;
    }

    div[data-testid="stAppViewContainer"] > .main > .block-container {
        padding-top: 60px;
    }

    button[kind="header"] { display: none !important; }
    section[data-testid="stSidebar"] { min-width: 280px; max-width: 320px; }
</style>
<div id="custom-header">
    <img src="/app/static/logo.svg" alt="Logo">
    <span class="title">АНАЛИЗ РИСКОВ</span>
</div>
""", unsafe_allow_html=True)

@st.cache_resource
def get_data():
    return load_all()

data = get_data()
df_cy = data["company_year"]
df_an = data["anomaly"]
df_hf = data["hypothesis_flags"]
df_gs = data["group_signal"]
df_hs = data["hypothesis_summary"]

# === SIDEBAR: Global Filters ===
with st.sidebar:
    st.header("Фильтры")

    years = sorted(df_cy["year"].unique())
    sel_year = st.selectbox("Год", years, index=len(years)-1, key="global_year")

    regions = sorted(df_cy["region"].dropna().unique())
    sel_regions = st.multiselect("Регион", regions, key="global_regions")

    sectors = sorted(df_cy["okved_section"].dropna().unique())
    sel_sectors = st.multiselect("Отрасль", sectors, key="global_sectors")

    st.divider()

    st.caption("Легенда")
    st.markdown('<span style="color:#FF4B4B">●</span> **Risk** — риск-аномалия', unsafe_allow_html=True)
    st.markdown('<span style="color:#4DA6FF">●</span> **Economic Signal** — экон. сигнал', unsafe_allow_html=True)
    st.markdown("Критичность:")
    for lbl, clr in [("critical", "#FF4B4B"), ("high", "#FF8C00"), ("medium", "#FFD700"), ("low", "#32CD32")]:
        st.markdown(f'<span style="color:{clr}; margin-left:12px">●</span> {lbl}', unsafe_allow_html=True)

    st.divider()

# Apply global filters
df_cy_filt = df_cy[df_cy["year"] == sel_year]
if sel_regions:
    df_cy_filt = df_cy_filt[df_cy_filt["region"].isin(sel_regions)]
if sel_sectors:
    df_cy_filt = df_cy_filt[df_cy_filt["okved_section"].isin(sel_sectors)]

_filtered_names = df_cy_filt["company_name"].dropna().unique().tolist()
df_an_filt = df_an[df_an["company_name"].isin(_filtered_names)]
df_hf_filt = df_hf[df_hf["company_name"].isin(_filtered_names)]

with st.sidebar:
    st.caption(f"Компаний: **{len(df_cy_filt)}** из {len(df_cy[df_cy['year']==sel_year])}")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Обзор",
    "Аномалии",
    "Профиль компании",
    "Групповые сигналы",
    "Гипотезы",
])

with tab1:
    from pages.tab_overview import render_overview
    render_overview(df_cy_filt, df_hs, data)

with tab2:
    from pages.tab_anomalies import render_anomalies
    render_anomalies(df_an_filt)

with tab3:
    from pages.tab_company import render_company
    render_company(df_cy, df_an, df_hf)

with tab4:
    from pages.tab_groups import render_groups
    render_groups(df_gs)

with tab5:
    from pages.tab_hypotheses import render_hypotheses
    render_hypotheses(df_hs, df_an_filt)
