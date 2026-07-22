import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.constants import CRITICALITY_COLORS

def render_groups(df_gs):
    st.sidebar.header("Фильтры групп")
    gtype = st.sidebar.multiselect("Тип группы", sorted(df_gs["group_type"].unique()), default=["founder", "address"], key="groups_type")
    crits = st.sidebar.multiselect("Критичность", sorted(df_gs["criticality_final"].unique()), default=sorted(df_gs["criticality_final"].unique()), key="groups_crit")
    
    df = df_gs[df_gs["group_type"].isin(gtype) & df_gs["criticality_final"].isin(crits)]
    
    st.markdown(f"### Групповые сигналы ({len(df)} групп)")
    
    # Rename columns for display
    display = df.rename(columns={
        "risk_companies_count": "Рисковых компаний",
        "signal_companies_count": "Сигнальных компаний",
        "anomaly_count": "Аномалий",
        "companies_count": "Компаний в группе",
    })
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Топ-20 групп по числу аномалий")
        top = df.nlargest(20, "anomaly_count")
        fig1 = px.bar(top, x="anomaly_count", y="group_key", orientation="h",
                       color="criticality_final", color_discrete_map=CRITICALITY_COLORS,
                       labels={"anomaly_count": "Аномалий", "group_key": "Группа"})
        fig1.update_layout(yaxis_categoryorder="total ascending")
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        st.markdown("#### Компаний vs Аномалий")
        fig2 = px.scatter(df, x="companies_count", y="anomaly_count", color="group_type",
                          size="max_criticality_score",
                          hover_data=["group_key", "interpretation_final"],
                          color_discrete_map={"founder": "#4DA6FF", "address": "#FF8C00"},
                          labels={"companies_count": "Компаний в группе", "anomaly_count": "Аномалий"})
        st.plotly_chart(fig2, use_container_width=True)
    
    st.markdown("#### Тип группы × Критичность")
    group_crit = df.groupby(["group_type", "criticality_final"]).size().reset_index(name="count")
    fig3 = px.bar(group_crit, x="group_type", y="count", color="criticality_final",
                   color_discrete_map=CRITICALITY_COLORS, barmode="stack",
                   labels={"group_type": "Тип группы", "count": "Групп", "criticality_final": "Критичность"})
    st.plotly_chart(fig3, use_container_width=True)
    
    st.markdown("#### Все группы")
    show_cols = ["group_key", "group_type", "companies_count", "risk_companies_count",
                 "signal_companies_count", "anomaly_count", "avg_criticality_score",
                 "max_criticality_score", "interpretation_final", "criticality_final",
                 "interpretation_reason_final"]
    st.dataframe(df[show_cols].sort_values("max_criticality_score", ascending=False),
                 use_container_width=True, hide_index=True,
                 column_config={
                     "avg_criticality_score": st.column_config.NumberColumn("Ср. балл", format="%.1f"),
                 })
