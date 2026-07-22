import streamlit as st
from utils.chart_builder import (
    sunburst_hypotheses, grouped_bar_hypothesis_companies,
    boxplot_zscore, pie_risk_vs_signal,
)


def render_hypotheses(df_hs, df_an):
    st.sidebar.header("Фильтры гипотез")
    hyps = st.sidebar.multiselect(
        "Гипотеза", sorted(df_hs["hypothesis_code"].unique()),
        default=sorted(df_hs["hypothesis_code"].unique()), key="hypotheses_hyps",
    )
    interp = st.sidebar.multiselect(
        "Интерпретация", sorted(df_hs["interpretation"].unique()),
        default=["risk", "economic_signal"], key="hypotheses_interp",
    )

    df = df_hs[df_hs["hypothesis_code"].isin(hyps) & df_hs["interpretation"].isin(interp)]

    st.markdown("### Гипотезы — глубокий анализ")

    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(sunburst_hypotheses(df), use_container_width=True)
    with col2:
        st.plotly_chart(grouped_bar_hypothesis_companies(df), use_container_width=True)

    st.markdown("#### Таблица сводки по гипотезам")
    display = df.copy()
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

    df_z = df_an[df_an["hypothesis_code"].isin(hyps)]
    st.plotly_chart(boxplot_zscore(df_z), use_container_width=True)
    st.plotly_chart(pie_risk_vs_signal(df), use_container_width=True)
