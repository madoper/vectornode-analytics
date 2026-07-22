import streamlit as st
from utils.constants import CRITICALITY_ORDER
from utils.chart_builder import top_groups_bar, scatter_groups, stacked_bar_group_criticality


def render_groups(df_gs):
    st.markdown(f"### Групповые сигналы ({len(df_gs)} групп)")

    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(top_groups_bar(df_gs), use_container_width=True)
    with col2:
        st.plotly_chart(scatter_groups(df_gs), use_container_width=True)

    st.plotly_chart(stacked_bar_group_criticality(df_gs), use_container_width=True)

    st.markdown("#### Все группы")
    show_cols = ["group_key", "group_type", "companies_count",
                  "risk_anomaly_count", "signal_anomaly_count", "anomaly_count",
                  "avg_criticality_score", "max_criticality_score", "criticality_final"]
    display = df_gs[show_cols].copy()
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
