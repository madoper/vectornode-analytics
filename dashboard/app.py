import streamlit as st
from utils.data_loader import load_all

st.set_page_config(page_title="АНАЛИЗ РИСКОВ", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
.stApp, .stApp > div, section[data-testid="stSidebar"] > div {
    background-color: #0E1117 !important;
}
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.header("Фильтры")
    st.selectbox("Тест", ["A", "B", "C"], key="test_box")
    st.multiselect("Тест2", ["X", "Y", "Z"], key="test_multi")

data = load_all()
df_cy = data["company_year"]
df_an = data["anomaly"]
df_hf = data["hypothesis_flags"]
df_gs = data["group_signal"]
df_hs = data["hypothesis_summary"]

st.write(f"Данные загружены: {df_cy.shape[0]} строк, {df_an.shape[0]} аномалий")

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
