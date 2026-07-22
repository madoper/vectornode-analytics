import streamlit as st
from utils.data_loader import load_all

st.set_page_config(page_title="АНАЛИЗ РИСКОВ", layout="wide")

# ── Theme toggle ──
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True

dark = st.toggle("Тёмная тема", value=st.session_state.dark_mode, key="theme_toggle")
st.session_state.dark_mode = dark

if dark:
    bg = "#0E1117"
    fg = "#FFFFFF"
    card_bg = "#1E1E1E"
    border = "#333"
else:
    bg = "#FFFFFF"
    fg = "#000000"
    card_bg = "#F0F2F6"
    border = "#DDD"

st.markdown(f"""
<style>
    .stApp, .stApp > div {{ background-color: {bg} !important; color: {fg} !important; }}
    div[data-testid="stMetricValue"] {{ color: {fg} !important; }}
    h1, h2, h3, h4, h5, h6, p, span, label {{ color: {fg} !important; }}
    .filter-card {{
        background: {card_bg}; padding: 16px; border-radius: 8px;
        border: 1px solid {border}; margin-bottom: 12px;
    }}
</style>
""", unsafe_allow_html=True)

data = load_all()
df_cy = data["company_year"]
df_an = data["anomaly"]
df_hf = data["hypothesis_flags"]
df_gs = data["group_signal"]
df_hs = data["hypothesis_summary"]

# ── Layout: main left, filters right ──
col_main, col_filters = st.columns([3.2, 1])

with col_filters:
    st.markdown(f'<div class="filter-card">', unsafe_allow_html=True)
    st.header("Фильтры")

    years = sorted(df_cy["year"].unique())
    sel_year = st.selectbox("Год", years, index=len(years) - 1, key="f_year")
    sel_regions = st.multiselect("Регион", sorted(df_cy["region"].dropna().unique()), key="f_regions")
    sel_sectors = st.multiselect("Отрасль", sorted(df_cy["okved_section"].dropna().unique()), key="f_sectors")

    hyps_all = sorted(df_an["hypothesis_code"].unique())
    sel_hyps = st.multiselect("Гипотеза", hyps_all, default=hyps_all, key="f_hyps")

    interps_all = sorted(df_an["interpretation"].unique())
    sel_interps = st.multiselect("Интерпретация", interps_all, default=interps_all, key="f_interps")

    crits_all = sorted(df_an["criticality"].unique())
    sel_crits = st.multiselect("Критичность", crits_all, default=crits_all, key="f_crits")

    st.markdown("---")
    st.caption("Легенда")
    st.markdown("🔴 Risk — риск-аномалия")
    st.markdown("🔵 Economic Signal — экон. сигнал")
    st.markdown("none / low / medium / high / critical")
    st.markdown("</div>", unsafe_allow_html=True)

# ── Apply filters ──
mask_cy = (df_cy["year"] == sel_year)
if sel_regions:
    mask_cy &= df_cy["region"].isin(sel_regions)
if sel_sectors:
    mask_cy &= df_cy["okved_section"].isin(sel_sectors)
df_cy_f = df_cy[mask_cy]

f_names = df_cy_f["company_name"].dropna().unique().tolist()
df_an_f = df_an[df_an["company_name"].isin(f_names)]
df_an_f = df_an_f[df_an_f["hypothesis_code"].isin(sel_hyps)]
df_an_f = df_an_f[df_an_f["interpretation"].isin(sel_interps)]
df_an_f = df_an_f[df_an_f["criticality"].isin(sel_crits)]

df_hf_f = df_hf[df_hf["company_name"].isin(f_names)]
df_hs_f = df_hs[df_hs["hypothesis_code"].isin(sel_hyps)]
df_hs_f = df_hs_f[df_hs_f["interpretation"].isin(sel_interps)]

# ── Tabs ──
with col_main:
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Обзор", "Аномалии", "Профиль компании", "Групповые сигналы", "Гипотезы",
    ])

    with tab1:
        from pages.tab_overview import render_overview
        render_overview(df_cy_f, df_hs_f)

    with tab2:
        from pages.tab_anomalies import render_anomalies
        render_anomalies(df_an_f)

    with tab3:
        from pages.tab_company import render_company
        render_company(df_cy, df_an, df_hf)

    with tab4:
        from pages.tab_groups import render_groups
        render_groups(df_gs_f)

    with tab5:
        from pages.tab_hypotheses import render_hypotheses
        render_hypotheses(df_hs_f, df_an_f)
