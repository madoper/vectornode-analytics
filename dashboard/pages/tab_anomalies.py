import streamlit as st
from utils.chart_builder import scatter_zscore, treemap_anomalies, grouped_bar_interpretation


def render_anomalies(df_an):
    st.sidebar.header("Фильтры аномалий")
    hyps = st.sidebar.multiselect(
        "Гипотеза", sorted(df_an["hypothesis_code"].unique()),
        default=sorted(df_an["hypothesis_code"].unique()), key="anomalies_hyps",
    )
    interp = st.sidebar.multiselect(
        "Интерпретация", sorted(df_an["interpretation"].unique()),
        default=["risk", "economic_signal"], key="anomalies_interp",
    )
    crits = st.sidebar.multiselect(
        "Критичность", sorted(df_an["criticality"].unique()),
        default=sorted(df_an["criticality"].unique()), key="anomalies_crit",
    )
    years = st.sidebar.multiselect(
        "Год", sorted(df_an["year"].unique()),
        default=sorted(df_an["year"].unique()), key="anomalies_years",
    )

    df = df_an[
        df_an["hypothesis_code"].isin(hyps)
        & df_an["interpretation"].isin(interp)
        & df_an["criticality"].isin(crits)
        & df_an["year"].isin(years)
    ]

    st.markdown(f"### Аномалии ({len(df)} записей)")

    col1, col2 = st.columns(2)
    with col1:
        df_z = df.dropna(subset=["zscore"]).copy()
        if not df_z.empty:
            st.plotly_chart(scatter_zscore(df_z), use_container_width=True)
        else:
            st.info("Нет данных с z-score")
    with col2:
        st.plotly_chart(treemap_anomalies(df), use_container_width=True)

    st.plotly_chart(grouped_bar_interpretation(df), use_container_width=True)

    st.markdown("#### Таблица аномалий")
    show_cols = ["company_name", "year", "hypothesis_code", "metric", "value", "zscore",
                  "criticality_score", "criticality", "interpretation", "interpretation_reason"]
    display_df = df[show_cols].copy()
    if "criticality_score" in display_df.columns:
        display_df = display_df.sort_values(["year", "criticality_score"], ascending=[False, False])
    else:
        _cmap = {"critical": 4, "high": 3, "medium": 2, "low": 1}
        display_df["_sort"] = display_df["criticality"].map(_cmap).fillna(0)
        display_df = display_df.sort_values(["year", "_sort"], ascending=[False, False]).drop(columns=["_sort"])
    st.dataframe(
        display_df, use_container_width=True, hide_index=True,
        column_config={
            "value": st.column_config.NumberColumn("Значение", format="%.2f"),
            "zscore": st.column_config.NumberColumn("Z-score", format="%.2f"),
        },
    )
