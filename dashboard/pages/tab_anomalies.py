import streamlit as st
from utils.chart_builder import scatter_zscore, treemap_anomalies, grouped_bar_interpretation


def render_anomalies(df_an):
    st.markdown(f"### Аномалии ({len(df_an)} записей)")

    col1, col2 = st.columns(2)
    with col1:
        df_z = df_an.dropna(subset=["zscore"]).copy()
        if not df_z.empty:
            st.plotly_chart(scatter_zscore(df_z), use_container_width=True)
        else:
            st.info("Нет данных с z-score")
    with col2:
        st.plotly_chart(treemap_anomalies(df_an), use_container_width=True)

    st.plotly_chart(grouped_bar_interpretation(df_an), use_container_width=True)

    st.markdown("#### Таблица аномалий")
    show_cols = ["company_name", "year", "hypothesis_code", "metric", "value", "zscore",
                  "criticality_score", "criticality", "interpretation", "interpretation_reason"]
    display_df = df_an[show_cols].copy()
    if "criticality_score" in display_df.columns:
        display_df = display_df.sort_values(["year", "criticality_score"], ascending=[False, False])
    else:
        display_df["_sort"] = display_df["criticality"].map({"critical": 4, "high": 3, "medium": 2, "low": 1}).fillna(0)
        display_df = display_df.sort_values(["year", "_sort"], ascending=[False, False]).drop(columns=["_sort"])
    st.dataframe(
        display_df, use_container_width=True, hide_index=True,
        column_config={
            "value": st.column_config.NumberColumn("Значение", format="%.2f"),
            "zscore": st.column_config.NumberColumn("Z-score", format="%.2f"),
        },
    )
