import streamlit as st
from utils.chart_builder import (
    sunburst_hypotheses, grouped_bar_hypothesis_companies,
    boxplot_zscore, pie_risk_vs_signal,
)


def render_hypotheses(df_hs, df_an):
    st.markdown("### Гипотезы — глубокий анализ")

    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(sunburst_hypotheses(df_hs), use_container_width=True)
    with col2:
        st.plotly_chart(grouped_bar_hypothesis_companies(df_hs), use_container_width=True)

    st.markdown("#### Таблица сводки по гипотезам")
    display = df_hs.copy()
    display["avg_findings_per_company"] = (display["findings_count"] / display["companies_count"]).round(1)
    show_cols = ["hypothesis_code", "interpretation", "criticality", "findings_count",
                  "companies_count", "company_year_count", "avg_findings_per_company"]
    st.dataframe(
        display[show_cols].sort_values("findings_count", ascending=False),
        use_container_width=True, hide_index=True,
        column_config={
            "avg_findings_per_company": st.column_config.NumberColumn("В ср. на компанию", format="%.1f"),
        },
    )

    st.plotly_chart(boxplot_zscore(df_an), use_container_width=True)
    st.plotly_chart(pie_risk_vs_signal(df_hs), use_container_width=True)
