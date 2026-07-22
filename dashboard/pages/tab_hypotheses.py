import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.constants import CRITICALITY_COLORS, INTERPRETATION_COLORS, HYPOTHESIS_LABELS

def render_hypotheses(df_hs, df_an):
    st.sidebar.header("Фильтры гипотез")
    hyps = st.sidebar.multiselect("Гипотеза", sorted(df_hs["hypothesis_code"].unique()), default=sorted(df_hs["hypothesis_code"].unique()), key="hypotheses_hyps")
    interp = st.sidebar.multiselect("Интерпретация", sorted(df_hs["interpretation"].unique()), default=["risk", "economic_signal"], key="hypotheses_interp")
    
    df = df_hs[df_hs["hypothesis_code"].isin(hyps) & df_hs["interpretation"].isin(interp)]
    
    st.markdown("### Гипотезы — глубокий анализ")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Sunburst: гипотезы → интерпретация → критичность")
        fig1 = px.sunburst(df, path=["hypothesis_code", "interpretation", "criticality"],
                            values="findings_count", color="criticality",
                            color_discrete_map=CRITICALITY_COLORS)
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        st.markdown("#### Уникальных компаний по гипотезам")
        fig2 = px.bar(df, x="hypothesis_code", y="companies_count", color="interpretation",
                       color_discrete_map=INTERPRETATION_COLORS, barmode="group",
                       labels={"hypothesis_code": "Гипотеза", "companies_count": "Уникальных компаний"})
        st.plotly_chart(fig2, use_container_width=True)
    
    st.markdown("#### Таблица сводки по гипотезам")
    display = df.copy()
    display["avg_per_company"] = (display["findings_count"] / display["companies_count"]).round(1)
    show_cols = ["hypothesis_code", "interpretation", "criticality", "findings_count",
                 "companies_count", "company_year_count", "avg_per_company"]
    st.dataframe(display[show_cols].sort_values("findings_count", ascending=False),
                 use_container_width=True, hide_index=True,
                 column_config={
                     "avg_per_company": st.column_config.NumberColumn("В ср. на компанию", format="%.1f"),
                 })
    
    # Box plot of zscore by hypothesis
    st.markdown("#### Box plot: Z-score по гипотезам")
    df_z = df_an.dropna(subset=["zscore"])
    df_z = df_z[df_z["hypothesis_code"].isin(hyps)]
    fig3 = px.box(df_z, x="hypothesis_code", y="zscore", color="interpretation",
                   color_discrete_map=INTERPRETATION_COLORS,
                   labels={"hypothesis_code": "Гипотеза", "zscore": "Z-score"})
    st.plotly_chart(fig3, use_container_width=True)
    
    # Pie chart
    st.markdown("#### Доля Risk vs Economic Signal")
    pie_data = df.groupby("interpretation")["findings_count"].sum().reset_index()
    fig4 = px.pie(pie_data, values="findings_count", names="interpretation",
                   color="interpretation", color_discrete_map=INTERPRETATION_COLORS,
                   hole=0.4)
    fig4.update_traces(textinfo="value+percent")
    st.plotly_chart(fig4, use_container_width=True)
