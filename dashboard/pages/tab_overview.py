import streamlit as st
from utils.chart_builder import kpi_card, donut_criticality, stacked_bar_hypotheses, heatmap_hypothesis_criticality, top_sectors_bar


def render_overview(df_cy, df_hs):
    total = len(df_cy)
    risk_count = int(df_cy["risk_flag"].sum())
    critical_count = int((df_cy["criticality_final"] == "critical").sum())
    anomaly_total = int(df_cy["anomaly_count"].sum())
    signal_only = int(df_cy["signal_only_flag"].sum())
    risk_pct = f"{risk_count / total * 100:.1f}%" if total else "0%"

    st.markdown("### Ключевые показатели")
    cols = st.columns(6)
    with cols[0]: st.markdown(kpi_card("Всего компаний", str(total), color="#4DA6FF"), unsafe_allow_html=True)
    with cols[1]: st.markdown(kpi_card("С риском", str(risk_count), color="#FF4B4B"), unsafe_allow_html=True)
    with cols[2]: st.markdown(kpi_card("Критические", str(critical_count), color="#FF0000"), unsafe_allow_html=True)
    with cols[3]: st.markdown(kpi_card("Всего аномалий", str(anomaly_total), color="#FFD700"), unsafe_allow_html=True)
    with cols[4]: st.markdown(kpi_card("Только сигналы", str(signal_only), color="#4DA6FF"), unsafe_allow_html=True)
    with cols[5]: st.markdown(kpi_card("Доля риска", risk_pct, color="#FF8C00"), unsafe_allow_html=True)

    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(donut_criticality(df_cy), use_container_width=True)
    with col2:
        st.plotly_chart(stacked_bar_hypotheses(df_hs), use_container_width=True)

    st.plotly_chart(heatmap_hypothesis_criticality(df_hs), use_container_width=True)
    st.plotly_chart(top_sectors_bar(df_cy), use_container_width=True)
