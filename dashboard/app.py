import streamlit as st
from utils.data_loader import load_all
from utils.constants import CRITICALITY_COLORS, CRITICALITY_ORDER, INTERPRETATION_COLORS, HYPOTHESIS_LABELS

st.set_page_config(
    page_title="АНАЛИЗ РИСКОВ",
    page_icon="logo.svg",
    layout="wide",
    initial_sidebar_state="expanded",
)

data = load_all()
df_cy = data["company_year"]
df_an = data["anomaly"]
df_hf = data["hypothesis_flags"]
df_gs = data["group_signal"]
df_hs = data["hypothesis_summary"]

# === SIDEBAR ===
st.sidebar.write("✅ Sidebar active")
st.sidebar.header("Фильтры")

# (A) Overview filters (year, region, sector) — apply to all tabs
years = sorted(df_cy["year"].unique())
sel_year = st.sidebar.selectbox("Год", years, index=len(years) - 1, key="g_year")
sel_regions = st.sidebar.multiselect("Регион", sorted(df_cy["region"].dropna().unique()), key="g_regions")
sel_sectors = st.sidebar.multiselect("Отрасль", sorted(df_cy["okved_section"].dropna().unique()), key="g_sectors")

# (B) Anomaly / hypothesis filters
hyps_all = sorted(data["anomaly"]["hypothesis_code"].unique())
sel_hyps = st.sidebar.multiselect("Гипотеза", hyps_all, default=hyps_all, key="g_hyps")

interps_all = sorted(data["anomaly"]["interpretation"].unique())
sel_interps = st.sidebar.multiselect("Интерпретация", interps_all, default=interps_all, key="g_interps")

crits_all = sorted(data["anomaly"]["criticality"].unique())
sel_crits = st.sidebar.multiselect("Критичность", crits_all, default=crits_all, key="g_crits")

st.sidebar.divider()

# === FILTER APPLICATION ===
# Company-year: year + region + sector
mask_cy = (df_cy["year"] == sel_year)
if sel_regions:
    mask_cy &= df_cy["region"].isin(sel_regions)
if sel_sectors:
    mask_cy &= df_cy["okved_section"].isin(sel_sectors)
df_cy_f = df_cy[mask_cy]

# Company names from filtered cy → use for anomaly/hf filtering
f_names = df_cy_f["company_name"].dropna().unique().tolist()

df_an_f = df_an[df_an["company_name"].isin(f_names)]
df_an_f = df_an_f[df_an_f["hypothesis_code"].isin(sel_hyps)]
df_an_f = df_an_f[df_an_f["interpretation"].isin(sel_interps)]
df_an_f = df_an_f[df_an_f["criticality"].isin(sel_crits)]

df_hf_f = df_hf[df_hf["company_name"].isin(f_names)]

df_hs_f = df_hs[df_hs["hypothesis_code"].isin(sel_hyps)]
df_hs_f = df_hs_f[df_hs_f["interpretation"].isin(sel_interps)]

# Group signal: filter by criticality only (no year/region on groups)
df_gs_f = df_gs[df_gs["criticality_final"].isin(sel_crits)]

st.sidebar.markdown(f"Компаний: **{len(df_cy_f)}**")
st.sidebar.divider()

# Legend
st.sidebar.caption("Легенда")
st.sidebar.markdown('<span style="color:#FF4B4B">●</span> Risk', unsafe_allow_html=True)
st.sidebar.markdown('<span style="color:#4DA6FF">●</span> Economic Signal', unsafe_allow_html=True)
st.sidebar.caption("none / low / medium / high / critical")

# === TABS ===
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
