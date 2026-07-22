import streamlit as st
from utils.data_loader import load_all

st.set_page_config(page_title="АНАЛИЗ РИСКОВ", layout="wide", initial_sidebar_state="expanded")

data = load_all()
df_cy = data["company_year"]
df_an = data["anomaly"]
df_hf = data["hypothesis_flags"]
df_gs = data["group_signal"]
df_hs = data["hypothesis_summary"]

st.sidebar.header("Фильтры")

years = sorted(int(x) for x in df_cy["year"].unique())
sel_year = st.sidebar.selectbox("Год", years, index=len(years) - 1, key="g_year")

regions = sorted(df_cy["region"].dropna().unique().tolist())
sel_region = st.sidebar.selectbox("Регион", ["Все"] + regions, index=0, key="g_region")

sectors = sorted(df_cy["okved_section"].dropna().unique().tolist())
sel_sector = st.sidebar.selectbox("Отрасль", ["Все"] + sectors, index=0, key="g_sector")

hyps_all = sorted(df_an["hypothesis_code"].unique().tolist())
sel_hyps = st.sidebar.multiselect("Гипотеза", hyps_all, default=hyps_all, key="g_hyps")

interps_all = sorted(df_an["interpretation"].unique().tolist())
sel_interps = st.sidebar.multiselect("Интерпретация", interps_all, default=interps_all, key="g_interps")

crits_all = sorted(df_an["criticality"].unique().tolist())
sel_crits = st.sidebar.multiselect("Критичность", crits_all, default=crits_all, key="g_crits")

st.sidebar.markdown(f"Компаний: **{len(df_cy)}**")
st.sidebar.divider()
st.sidebar.caption("Легенда")
st.sidebar.markdown("🔴 Risk — риск-аномалия")
st.sidebar.markdown("🔵 Economic Signal — экон. сигнал")
st.sidebar.caption("none / low / medium / high / critical")

mask_cy = (df_cy["year"] == sel_year)
if sel_region != "Все":
    mask_cy &= df_cy["region"] == sel_region
if sel_sector != "Все":
    mask_cy &= df_cy["okved_section"] == sel_sector
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
