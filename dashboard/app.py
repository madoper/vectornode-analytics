import streamlit as st
from utils.data_loader import load_all
from utils.constants import CRITICALITY_COLORS, CRITICALITY_ORDER, INTERPRETATION_COLORS, HYPOTHESIS_LABELS

st.set_page_config(
    page_title="АНАЛИЗ РИСКОВ",
    page_icon="logo.svg",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    .stApp { background-color: #0E1117; }
    div[data-testid="stMetricValue"] { color: #FFFFFF !important; }

    /* Keep header functional but transparent */
    header[data-testid="stHeader"] {
        background-color: transparent !important;
        height: 56px !important;
        z-index: 10000 !important;
    }
    header[data-testid="stHeader"] [data-testid="stToolbar"] {
        display: none !important;
    }

    footer { visibility: hidden !important; }

    section[data-testid="stSidebar"] { min-width: 260px !important; }
    section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p:last-child {
        display: none;
    }

    /* Custom header overlay */
    #custom-header {
        position: fixed;
        top: 0; left: 0; right: 0;
        height: 56px;
        background-color: #0E1117;
        display: flex;
        align-items: center;
        padding: 0 16px;
        z-index: 9999;
        border-bottom: 1px solid #333;
        pointer-events: none;
    }
    #custom-header img { height: 40px; width: 40px; }
    #custom-header .title {
        position: absolute; left: 50%; transform: translateX(-50%);
        font-size: 20px; font-weight: 700; letter-spacing: 3px;
        color: #FFFFFF; white-space: nowrap;
    }

    /* Main content offset */
    section[data-testid="stMain"] > div { padding-top: 60px !important; }

    /* Sticky tabs */
    div[data-testid="stTabs"] {
        position: sticky !important;
        top: 56px !important;
        z-index: 998 !important;
        background-color: #0E1117 !important;
        padding-top: 4px; padding-bottom: 4px;
        border-bottom: 1px solid #333;
        margin-bottom: 12px;
    }
    div[data-testid="stTabs"] button { font-size: 14px; }
</style>
<div id="custom-header">
    <img src="/app/static/logo.svg" alt="Logo">
    <span class="title">АНАЛИЗ РИСКОВ</span>
</div>
""", unsafe_allow_html=True)

# JS diagnostics — dump key selectors at startup
st.markdown("""
<script>
(function() {
    const els = [];
    const selectors = [
        "header[data-testid='stHeader']",
        "section[data-testid='stSidebar']",
        "div[data-testid='stTabs']",
        "section[data-testid='stMain']",
        "section[data-testid='stMain'] > div",
        "button[kind='header']",
        "[data-testid='stSidebarCollapseButton']",
        ".st-emotion-cache-1gwvycy",
        "footer",
    ];
    for (const sel of selectors) {
        const el = document.querySelector(sel);
        els.push(sel + " => " + (el ? el.tagName + (el.id ? "#" + el.id : "") : "NOT FOUND"));
    }
    const dump = document.createElement("details");
    dump.style.cssText = "font-size:11px;color:#888;margin:4px;";
    dump.innerHTML = "<summary>DOM diagnostics</summary><pre>" + els.join("\\n") + "</pre>";
    document.body.appendChild(dump);
})();
</script>
""", unsafe_allow_html=True)

data = load_all()
df_cy = data["company_year"]
df_an = data["anomaly"]
df_hf = data["hypothesis_flags"]
df_gs = data["group_signal"]
df_hs = data["hypothesis_summary"]

tab1, tab2, tab3, tab4, tab5 = st.tabs(["Обзор", "Аномалии", "Профиль компании", "Групповые сигналы", "Гипотезы"])

with tab1:
    from pages.tab_overview import render_overview
    render_overview(df_cy, df_hs)

with tab2:
    from pages.tab_anomalies import render_anomalies
    render_anomalies(df_an)

with tab3:
    from pages.tab_company import render_company
    render_company(df_cy, df_an, df_hf)

with tab4:
    from pages.tab_groups import render_groups
    render_groups(df_gs)

with tab5:
    from pages.tab_hypotheses import render_hypotheses
    render_hypotheses(df_hs, df_an)
