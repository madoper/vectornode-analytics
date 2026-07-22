import streamlit as st
import pandas as pd
from utils.constants import CRITICALITY_COLORS, CRITICALITY_ORDER
from utils.charts import kpi_card

def render_overview(df_cy, df_hs, data):
    latest = df_cy[df_cy["is_latest_year"] == 1]
    
    df = df_cy
    
    total = len(df)
    risk_count = int(df["risk_flag"].sum())
    critical_count = int((df["criticality_final"] == "critical").sum())
    anomaly_total = int(df["anomaly_count"].sum())
    signal_only = int(df["signal_only_flag"].sum())
    risk_pct = f"{risk_count / total * 100:.1f}%" if total else "0%"
    
    # KPI cards
    st.markdown("### Ключевые показатели")
    cols = st.columns(6)
    with cols[0]: st.markdown(kpi_card("Всего компаний", str(total), color="#4DA6FF"), unsafe_allow_html=True)
    with cols[1]: st.markdown(kpi_card("С риском", str(risk_count), color="#FF4B4B"), unsafe_allow_html=True)
    with cols[2]: st.markdown(kpi_card("Критические", str(critical_count), color="#FF0000"), unsafe_allow_html=True)
    with cols[3]: st.markdown(kpi_card("Всего аномалий", str(anomaly_total), color="#FFD700"), unsafe_allow_html=True)
    with cols[4]: st.markdown(kpi_card("Только сигналы", str(signal_only), color="#4DA6FF"), unsafe_allow_html=True)
    with cols[5]: st.markdown(kpi_card("Доля риска", risk_pct, color="#FF8C00"), unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Charts row 1
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Распределение критичности")
        crit_counts = df["criticality_final"].value_counts()
        crit_order = [c for c in CRITICALITY_ORDER if c in crit_counts.index]
        import plotly.express as px
        fig1 = px.pie(values=[crit_counts.get(c, 0) for c in crit_order],
                       names=crit_order, hole=0.5,
                       color=crit_order, color_discrete_map=CRITICALITY_COLORS)
        fig1.update_traces(textinfo="value+percent")
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        st.markdown("#### Аномалии по гипотезам")
        import plotly.express as px
        fig2 = px.bar(df_hs, x="hypothesis_code", y="findings_count", color="interpretation",
                       color_discrete_map={"risk": "#FF4B4B", "economic_signal": "#4DA6FF"},
                       labels={"hypothesis_code": "Гипотеза", "findings_count": "Находок", "interpretation": "Тип"},
                       barmode="stack")
        st.plotly_chart(fig2, use_container_width=True)
    
    # Charts row 2
    st.markdown("#### Тепловая карта: гипотезы × критичность")
    heat = df_hs.pivot_table(values="findings_count", index="hypothesis_code",
                              columns="criticality", aggfunc="sum", fill_value=0)
    fig3 = px.imshow(heat, text_auto=True, aspect="auto", color_continuous_scale="Reds",
                      labels={"x": "Критичность", "y": "Гипотеза", "color": "Находок"})
    st.plotly_chart(fig3, use_container_width=True)
    
    st.markdown("#### Топ-10 отраслей по рисковым компаниям")
    sector_risk = df[df["risk_flag"] == 1].groupby("okved_section").size().sort_values(ascending=False).head(10)
    fig4 = px.bar(x=sector_risk.values, y=sector_risk.index, orientation="h",
                   color=sector_risk.values, color_continuous_scale="Reds",
                   labels={"x": "Рисковых компаний", "y": "Отрасль"})
    fig4.update_layout(showlegend=False, yaxis_categoryorder="total ascending")
    st.plotly_chart(fig4, use_container_width=True)
