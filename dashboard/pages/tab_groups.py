import streamlit as st
from utils.chart_builder import top_groups_bar, scatter_groups, stacked_bar_group_criticality
from utils.constants import CRITICALITY_ORDER


def render_groups(df_gs):
    gtypes = sorted(df_gs["group_type"].unique())
    gcrits = sorted(df_gs["criticality_final"].unique(), key=lambda c: CRITICALITY_ORDER.index(c) if c in CRITICALITY_ORDER else 99)

    st.sidebar.header("Фильтры групп")
    sel_types = st.sidebar.multiselect("Тип группы", gtypes, default=gtypes, key="groups_type")
    sel_crits = st.sidebar.multiselect("Критичность", gcrits, default=gcrits, key="groups_crit")

    df = df_gs[df_gs["group_type"].isin(sel_types) & df_gs["criticality_final"].isin(sel_crits)]

    st.markdown(f"### Групповые сигналы ({len(df)} групп)")

    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(top_groups_bar(df), use_container_width=True)
    with col2:
        st.plotly_chart(scatter_groups(df), use_container_width=True)

    st.plotly_chart(stacked_bar_group_criticality(df), use_container_width=True)

    st.markdown("#### Все группы")
    show_cols = ["group_key", "group_type", "companies_count",
                  "risk_anomaly_count", "signal_anomaly_count", "anomaly_count",
                  "avg_criticality_score", "max_criticality_score", "criticality_final"]
    display = df[show_cols].copy()
    display = display.rename(columns={
        "risk_anomaly_count": "Рисковые аномалии",
        "signal_anomaly_count": "Сигнальные аномалии",
        "anomaly_count": "Аномалий",
        "companies_count": "Компаний",
        "avg_criticality_score": "Ср. балл",
        "max_criticality_score": "Макс. балл",
        "criticality_final": "Критичность",
        "group_key": "Группа",
        "group_type": "Тип",
    })
    st.dataframe(
        display.sort_values("Макс. балл", ascending=False),
        use_container_width=True, hide_index=True,
        column_config={
            "Ср. балл": st.column_config.NumberColumn("Ср. балл", format="%.1f"),
        },
    )
