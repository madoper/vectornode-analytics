import streamlit as st
from utils.data_loader import load_all

st.set_page_config(page_title="АНАЛИЗ РИСКОВ", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    .stApp { background-color: #0E1117; }
    footer { visibility: hidden; }

    /* Sidebar always expanded — non-collapsible */
    section[data-testid="stSidebar"] {
        z-index: 100 !important;
        min-width: 300px !important;
        width: auto !important;
    }

    /* Hide the collapse button only */
    [data-testid="stSidebarCollapseButton"] {
        display: none !important;
    }
</style>
""", unsafe_allow_html=True)

data = load_all()
df_cy = data["company_year"]
df_an = data["anomaly"]
df_hf = data["hypothesis_flags"]
df_gs = data["group_signal"]
df_hs = data["hypothesis_summary"]

# ── Sidebar filters ──
with st.sidebar:
    st.header("Фильтры")

    years = sorted(int(x) for x in df_cy["year"].unique())
    sel_year = st.selectbox("Год", years, index=len(years) - 1, key="g_year")

    hyps_all = sorted(df_an["hypothesis_code"].unique().tolist())
    sel_hyps = st.multiselect("Гипотеза", hyps_all, default=hyps_all, key="g_hyps")

    interps_all = sorted(df_an["interpretation"].unique().tolist())
    sel_interps = st.multiselect("Интерпретация", interps_all, default=interps_all, key="g_interps")

    crits_all = sorted(df_an["criticality"].unique().tolist())
    sel_crits = st.multiselect("Критичность", crits_all, default=crits_all, key="g_crits")

    # Region and Sector — diagnostic: simple write first
    regions = df_cy["region"].dropna().unique().tolist()
    st.write(f"Регионов: {len(regions)}")
    sectors = df_cy["okved_section"].dropna().unique().tolist()
    st.write(f"Отраслей: {len(sectors)}")
    sel_regions = st.multiselect("Регион", regions, default=regions[:3], key="g_regions")
    sel_sectors = st.multiselect("Отрасль", sectors, default=sectors[:3], key="g_sectors")

    st.markdown(f"Компаний: **{len(df_cy)}**")
    st.divider()
    st.caption("Легенда")
    st.markdown("🔴 Risk — риск-аномалия")
    st.markdown("🔵 Economic Signal — экон. сигнал")
    st.caption("none / low / medium / high / critical")

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

tab1, tab2, tab3, tab4, tab5 = st.tabs(["Обзор", "Аномалии", "Профиль компании", "Групповые сигналы", "Гипотезы"])

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
