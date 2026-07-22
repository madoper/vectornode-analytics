import streamlit as st
import pandas as pd
from utils.constants import CRITICALITY_COLORS, INTERPRETATION_COLORS

def render_anomalies(df_an):
    st.sidebar.header("Фильтры аномалий")
    hyps = st.sidebar.multiselect("Гипотеза", sorted(df_an["hypothesis_code"].unique()), default=sorted(df_an["hypothesis_code"].unique()), key="anomalies_hyps")
    interp = st.sidebar.multiselect("Интерпретация", sorted(df_an["interpretation"].unique()), default=["risk", "economic_signal"], key="anomalies_interp")
    crits = st.sidebar.multiselect("Критичность", sorted(df_an["criticality"].unique()), default=sorted(df_an["criticality"].unique()), key="anomalies_crit")
    years = st.sidebar.multiselect("Год", sorted(df_an["year"].unique()), default=sorted(df_an["year"].unique()), key="anomalies_years")
    
    df = df_an[
        df_an["hypothesis_code"].isin(hyps) &
        df_an["interpretation"].isin(interp) &
        df_an["criticality"].isin(crits) &
        df_an["year"].isin(years)
    ]
    
    st.markdown(f"### Аномалии ({len(df)} записей)")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Scatter: Z-score × Критичность")
        df_plot = df.dropna(subset=["zscore"]).copy()
        if not df_plot.empty:
            import plotly.express as px
            fig1 = px.scatter(df_plot, x="zscore", y="criticality_score", color="hypothesis_code",
                             size=df_plot["value"].abs().clip(upper=df_plot["value"].abs().quantile(0.90)),
                             hover_data=["company_name", "year", "metric", "interpretation_reason"],
                             labels={"zscore": "Z-score", "criticality_score": "Балл критичности"})
            st.plotly_chart(fig1, use_container_width=True)
        else:
            st.info("Нет данных с z-score")
    
    with col2:
        st.markdown("#### Treemap: гипотезы → критичность")
        tree = df.groupby(["hypothesis_code", "criticality", "interpretation"]).size().reset_index(name="count")
        import plotly.express as px
        fig2 = px.treemap(tree, path=["hypothesis_code", "criticality", "interpretation"],
                           values="count", color="criticality",
                           color_discrete_map=CRITICALITY_COLORS)
        st.plotly_chart(fig2, use_container_width=True)
    
    st.markdown("#### Распределение по гипотезам")
    bar_data = df.groupby(["hypothesis_code", "interpretation"]).size().reset_index(name="count")
    fig3 = px.bar(bar_data, x="hypothesis_code", y="count", color="interpretation",
                   color_discrete_map=INTERPRETATION_COLORS, barmode="group",
                   labels={"hypothesis_code": "Гипотеза", "count": "Находок"})
    st.plotly_chart(fig3, use_container_width=True)
    
    st.markdown("#### Таблица аномалий")
    show_cols = ["company_name", "year", "hypothesis_code", "metric", "value", "zscore",
                 "criticality", "interpretation", "interpretation_reason"]
    crit_sort = {"critical": 4, "high": 3, "medium": 2, "low": 1}
    display_df = df[show_cols].copy()
    if "criticality_score" in display_df.columns:
        display_df = display_df.sort_values(["criticality_score", "hypothesis_code"], ascending=[False, True])
    else:
        display_df["_sort"] = display_df["criticality"].map(crit_sort).fillna(0)
        display_df = display_df.sort_values(["_sort", "hypothesis_code"], ascending=[False, True]).drop(columns=["_sort"])
    st.dataframe(display_df, use_container_width=True, hide_index=True,
                 column_config={
                     "value": st.column_config.NumberColumn("Значение", format="%.2f"),
                     "zscore": st.column_config.NumberColumn("Z-score", format="%.2f"),
                 })
