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

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Обзор",
    "Аномалии",
    "Профиль компании",
    "Групповые сигналы",
    "Гипотезы",
])

# ===== TAB 1: OVERVIEW =====
with tab1:
    from pages.tab_overview import render_overview
    render_overview(df_cy, df_hs, data)

# ===== TAB 2: ANOMALIES =====
with tab2:
    from pages.tab_anomalies import render_anomalies
    render_anomalies(df_an)

# ===== TAB 3: COMPANY PROFILE =====
with tab3:
    from pages.tab_company import render_company
    render_company(df_cy, df_an, df_hf)

# ===== TAB 4: GROUP SIGNALS =====
with tab4:
    from pages.tab_groups import render_groups
    render_groups(df_gs)

# ===== TAB 5: HYPOTHESES =====
with tab5:
    from pages.tab_hypotheses import render_hypotheses
    render_hypotheses(df_hs, df_an)
