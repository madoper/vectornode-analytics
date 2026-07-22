import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.constants import CRITICALITY_COLORS, CRITICALITY_ORDER
from utils.charts import kpi_card, line_chart, radar_zscores

def render_company(df_cy, df_an, df_hf):
    companies = sorted(df_cy["company_name"].dropna().unique())
    sel_company = st.sidebar.selectbox("Компания", companies)
    
    cy = df_cy[df_cy["company_name"] == sel_company].sort_values("year")
    an = df_an[df_an["company_name"] == sel_company].sort_values("year")
    hf = df_hf[df_hf["company_name"] == sel_company].sort_values("year")
    
    if cy.empty:
        st.warning("Нет данных")
        return
    
    last = cy.iloc[-1]
    st.markdown(f"## {sel_company}")
    st.markdown(f"**{last['region']}** | **{last['okved_section']}** | ID: **{last['company_id']}**")
    
    # KPI
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
    
    # Financial trends
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Выручка, прибыль, дивиденды")
        fig1 = go.Figure()
        fig1.add_trace(go.Bar(x=cy["year"], y=cy["revenue"] / 1_000_000, name="Выручка (млн)", marker_color="#4DA6FF"))
        fig1.add_trace(go.Scatter(x=cy["year"], y=cy["net_profit"] / 1_000_000, name="Чистая прибыль (млн)",
                                   line=dict(color="#32CD32", width=3), mode="lines+markers"))
        fig1.add_trace(go.Scatter(x=cy["year"], y=cy["dividends_paid"] / 1_000_000, name="Дивиденды (млн)",
                                   line=dict(color="#FF4B4B", width=2, dash="dot"), mode="lines+markers"))
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        st.markdown("#### Маржа и финансовое давление")
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=cy["year"], y=cy["net_margin"] * 100, name="Чистая маржа %",
                                   line=dict(color="#4DA6FF", width=3), mode="lines+markers"))
        fig2.add_trace(go.Scatter(x=cy["year"], y=cy["financial_pressure_ratio"], name="FPR",
                                   line=dict(color="#FF8C00", width=2), mode="lines+markers", yaxis="y2"))
        fig2.update_layout(yaxis2=dict(overlaying="y", side="right"))
        st.plotly_chart(fig2, use_container_width=True)
    
    # Anomaly count by year
    st.markdown("#### Аномалии по годам")
    anomaly_by_year = cy[["year", "anomaly_count", "criticality_final"]]
    fig3 = px.bar(anomaly_by_year, x="year", y="anomaly_count", color="criticality_final",
                   color_discrete_map=CRITICALITY_COLORS,
                   labels={"anomaly_count": "Число аномалий", "year": "Год"})
    st.plotly_chart(fig3, use_container_width=True)
    
    # H1-H6 heatmap
    st.markdown("#### Матрица флагов H1–H6")
    heat_cols = [f"h{i}_flag" for i in range(1, 7)]
    heat_labels = [f"H{i}" for i in range(1, 7)]
    heat_data = hf[["year"] + heat_cols].set_index("year")
    heat_data.columns = heat_labels
    fig4 = px.imshow(heat_data.T, text_auto=True, aspect="auto", color_continuous_scale="RdYlGn",
                      labels={"x": "Год", "y": "Гипотеза", "color": "Флаг"})
    st.plotly_chart(fig4, use_container_width=True)
    
    # Radar z-scores
    st.markdown("#### Радар Z-скоров (последний год)")
    fig5 = radar_zscores(last, f"Z-scores для {sel_company} ({int(last['year'])})")
    st.plotly_chart(fig5, use_container_width=True)
    
    # Anomaly table
    st.markdown("#### Детализация аномалий")
    show_cols = ["year", "hypothesis_code", "metric", "value", "zscore",
                 "criticality", "interpretation", "interpretation_reason"]
    crit_sort = {"critical": 4, "high": 3, "medium": 2, "low": 1}
    display_an = an[show_cols].copy()
    if "criticality_score" in an.columns:
        display_an = display_an.join(an["criticality_score"])
        display_an = display_an.sort_values(["year", "criticality_score"], ascending=[False, False])
    else:
        display_an["_sort"] = display_an["criticality"].map(crit_sort).fillna(0)
        display_an = display_an.sort_values(["year", "_sort"], ascending=[False, False]).drop(columns=["_sort"])
    st.dataframe(display_an, use_container_width=True, hide_index=True)
