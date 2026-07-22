import streamlit as st
import pandas as pd
from utils.constants import CRITICALITY_COLORS
from utils.chart_builder import (
    kpi_card, line_financial_trends, line_margin_pressure,
    bar_anomalies_by_year, heatmap_flags, radar_zscores,
)


def render_company(df_cy, df_an, df_hf):
    companies = sorted(df_cy["company_name"].dropna().unique())
    if not companies:
        st.warning("Нет данных о компаниях")
        return
    sel_company = st.sidebar.selectbox("Компания", companies)

    cy = df_cy[df_cy["company_name"] == sel_company].sort_values("year")
    an = df_an[df_an["company_name"] == sel_company].sort_values("year")
    hf = df_hf[df_hf["company_name"] == sel_company].sort_values("year")

    if cy.empty:
        st.warning("Нет данных")
        return

    last = cy.iloc[-1]
    st.markdown(f"## {sel_company}")
    st.markdown(f"**{last.get('region','')}** | **{last.get('okved_section','')}** | ID: **{last['company_id']}**")

    cols = st.columns(6)
    with cols[0]: st.markdown(kpi_card("Выручка", f"{last['revenue']/1_000_000:,.0f} млн", color="#4DA6FF"), unsafe_allow_html=True)
    with cols[1]: st.markdown(kpi_card("Чистая прибыль", f"{last['net_profit']/1_000_000:,.1f} млн",
                                        color="#32CD32" if last['net_profit'] > 0 else "#FF4B4B"), unsafe_allow_html=True)
    with cols[2]: st.markdown(kpi_card("Маржа", f"{last['net_margin']*100:.1f}%", color="#FFD700"), unsafe_allow_html=True)
    with cols[3]: st.markdown(kpi_card("Сотрудников", str(int(last['headcount'])), color="#808080"), unsafe_allow_html=True)
    with cols[4]: st.markdown(kpi_card("Аномалий", str(int(last['anomaly_count'])),
                                        color=CRITICALITY_COLORS.get(last['criticality_final'], "#808080")), unsafe_allow_html=True)
    with cols[5]: st.markdown(kpi_card("Критичность", last['criticality_final'].upper(),
                                        color=CRITICALITY_COLORS.get(last['criticality_final'], "#808080")), unsafe_allow_html=True)

    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(line_financial_trends(cy), use_container_width=True)
    with col2:
        st.plotly_chart(line_margin_pressure(cy), use_container_width=True)

    st.plotly_chart(bar_anomalies_by_year(cy), use_container_width=True)

    st.markdown("#### Матрица флагов H1–H6")
    st.plotly_chart(heatmap_flags(hf), use_container_width=True)

    st.markdown("#### Радар Z-скоров (последний год)")
    st.plotly_chart(radar_zscores(last, f"Z-scores для {sel_company} ({int(last['year'])})"), use_container_width=True)

    st.markdown("#### Детализация аномалий")
    show_cols = ["year", "hypothesis_code", "metric", "value", "zscore",
                  "criticality", "interpretation", "interpretation_reason"]
    display_an = an[show_cols].copy() if not an.empty else pd.DataFrame()
    if not display_an.empty:
        if "criticality_score" in an.columns:
            display_an = display_an.join(an["criticality_score"])
        display_an = display_an.sort_values(["year", "criticality_score" if "criticality_score" in an.columns else "criticality"],
                                             ascending=[False, False])
        st.dataframe(display_an, use_container_width=True, hide_index=True)
