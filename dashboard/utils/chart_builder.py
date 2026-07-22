import plotly.express as px
import plotly.graph_objects as go
from .constants import CRITICALITY_COLORS, CRITICALITY_ORDER, INTERPRETATION_COLORS, HYPOTHESIS_LABELS


def kpi_card(label, value, color="#FFFFFF"):
    card_style = f"background:#1E1E1E;padding:16px;border-radius:8px;border-left:4px solid {color};margin:4px;"
    html = f'<div style="{card_style}"><small style="color:#AAA">{label}</small><br>'
    html += f'<span style="font-size:24px;font-weight:bold;color:#FFF">{value}</span></div>'
    return html


def donut_criticality(df, col="criticality_final", title="Распределение критичности"):
    crit_order = [c for c in CRITICALITY_ORDER if c in df[col].values]
    counts = df[col].value_counts().reindex(crit_order, fill_value=0)
    fig = px.pie(
        values=counts.values, names=counts.index, hole=0.5,
        color=counts.index, color_discrete_map=CRITICALITY_COLORS,
        title=title,
    )
    fig.update_traces(textinfo="value+percent")
    return fig


def stacked_bar_hypotheses(df_hs, title="Аномалии по гипотезам"):
    fig = px.bar(
        df_hs, x="hypothesis_code", y="findings_count", color="interpretation",
        color_discrete_map=INTERPRETATION_COLORS,
        labels={"hypothesis_code": "Гипотеза", "findings_count": "Находок", "interpretation": "Тип"},
        barmode="stack", title=title,
    )
    return fig


def heatmap_hypothesis_criticality(df_hs, title="Гипотезы × Критичность"):
    pivot = df_hs.pivot_table(
        values="findings_count", index="hypothesis_code",
        columns="criticality", aggfunc="sum", fill_value=0,
    )
    fig = px.imshow(
        pivot, text_auto=True, aspect="auto", color_continuous_scale="Reds",
        labels={"x": "Критичность", "y": "Гипотеза", "color": "Находок"},
        title=title,
    )
    return fig


def top_sectors_bar(df, title="Топ-10 отраслей по рисковым компаниям"):
    sector_risk = df[df["risk_flag"] == 1].groupby("okved_section").size().sort_values(ascending=False).head(10)
    fig = px.bar(
        x=sector_risk.values, y=sector_risk.index, orientation="h",
        color=sector_risk.values, color_continuous_scale="Reds",
        labels={"x": "Рисковых компаний", "y": "Отрасль"},
        title=title,
    )
    fig.update_layout(showlegend=False, yaxis_categoryorder="total ascending")
    return fig


def scatter_zscore(df, title="Z-score × Критичность"):
    fig = px.scatter(
        df, x="zscore", y="criticality_score", color="hypothesis_code",
        size=df["value"].abs().clip(upper=df["value"].abs().quantile(0.95)),
        hover_data=["company_name", "year", "metric", "interpretation_reason"],
        labels={"zscore": "Z-score", "criticality_score": "Балл критичности"},
        title=title,
    )
    return fig


def treemap_anomalies(df, title="Treemap: гипотезы → критичность → интерпретация"):
    tree = df.groupby(["hypothesis_code", "criticality", "interpretation"]).size().reset_index(name="count")
    fig = px.treemap(
        tree, path=["hypothesis_code", "criticality", "interpretation"],
        values="count", color="criticality",
        color_discrete_map=CRITICALITY_COLORS, title=title,
    )
    return fig


def grouped_bar_interpretation(df, x_col="hypothesis_code", y_col="count",
                                title="Распределение по гипотезам"):
    bar_data = df.groupby([x_col, "interpretation"]).size().reset_index(name=y_col)
    fig = px.bar(
        bar_data, x=x_col, y=y_col, color="interpretation",
        color_discrete_map=INTERPRETATION_COLORS, barmode="group",
        labels={x_col: "Гипотеза", y_col: "Находок"},
        title=title,
    )
    return fig


def line_financial_trends(df, x="year", title="Выручка, прибыль, дивиденды"):
    fig = go.Figure()
    fig.add_trace(go.Bar(x=df[x], y=df["revenue"] / 1_000_000, name="Выручка (млн)", marker_color="#4DA6FF"))
    fig.add_trace(go.Scatter(x=df[x], y=df["net_profit"] / 1_000_000, name="Чистая прибыль (млн)",
                              line=dict(color="#32CD32", width=3), mode="lines+markers"))
    fig.add_trace(go.Scatter(x=df[x], y=df["dividends_paid"] / 1_000_000, name="Дивиденды (млн)",
                              line=dict(color="#FF4B4B", width=2, dash="dot"), mode="lines+markers"))
    fig.update_layout(title=title, hovermode="x")
    return fig


def line_margin_pressure(df, x="year", title="Маржа и финансовое давление"):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df[x], y=df["net_margin"] * 100, name="Чистая маржа %",
                              line=dict(color="#4DA6FF", width=3), mode="lines+markers"))
    fig.add_trace(go.Scatter(x=df[x], y=df["financial_pressure_ratio"], name="FPR",
                              line=dict(color="#FF8C00", width=2), mode="lines+markers", yaxis="y2"))
    fig.update_layout(title=title, hovermode="x", yaxis2=dict(overlaying="y", side="right"))
    return fig


def bar_anomalies_by_year(df, title="Аномалии по годам"):
    fig = px.bar(
        df, x="year", y="anomaly_count", color="criticality_final",
        color_discrete_map=CRITICALITY_COLORS,
        labels={"anomaly_count": "Число аномалий", "year": "Год"},
        title=title,
    )
    return fig


def heatmap_flags(df_hf, title="Матрица флагов H1–H6"):
    heat_cols = [f"h{i}_flag" for i in range(1, 7)]
    heat_labels = [f"H{i}" for i in range(1, 7)]
    heat_data = df_hf[["year"] + heat_cols].set_index("year")
    heat_data.columns = heat_labels
    fig = px.imshow(
        heat_data.T, text_auto=True, aspect="auto", color_continuous_scale="RdYlGn",
        labels={"x": "Год", "y": "Гипотеза", "color": "Флаг"},
        title=title,
    )
    return fig


def radar_zscores(row, title="Радар Z-скоров"):
    cats = ["net_margin_z", "rev_per_emp_z", "financial_pressure_z", "rev_growth_z", "emp_growth_z"]
    labels = ["Маржа", "Выручка/сотр", "Фин. давление", "Рост выручки", "Рост числ-ти"]
    values = [row.get(c, 0) or 0 for c in cats]
    fig = go.Figure(go.Scatterpolar(r=values, theta=labels, fill="toself", name="Z-score"))
    fig.update_layout(title=title, polar=dict(radialaxis=dict(visible=True, range=[-4, 4])))
    return fig


def top_groups_bar(df, n=20, title="Топ-20 групп по числу аномалий"):
    top = df.nlargest(n, "anomaly_count")
    fig = px.bar(
        top, x="anomaly_count", y="group_key", orientation="h",
        color="criticality_final", color_discrete_map=CRITICALITY_COLORS,
        labels={"anomaly_count": "Аномалий", "group_key": "Группа"},
        title=title,
    )
    fig.update_layout(yaxis_categoryorder="total ascending")
    return fig


def scatter_groups(df, title="Компаний vs Аномалий"):
    fig = px.scatter(
        df, x="companies_count", y="anomaly_count", color="group_type",
        size="max_criticality_score",
        hover_data=["group_key"],
        color_discrete_map={"founder": "#4DA6FF", "address": "#FF8C00"},
        labels={"companies_count": "Компаний в группе", "anomaly_count": "Аномалий"},
        title=title,
    )
    return fig


def stacked_bar_group_criticality(df, title="Тип группы × Критичность"):
    group_crit = df.groupby(["group_type", "criticality_final"]).size().reset_index(name="count")
    fig = px.bar(
        group_crit, x="group_type", y="count", color="criticality_final",
        color_discrete_map=CRITICALITY_COLORS, barmode="stack",
        labels={"group_type": "Тип группы", "count": "Групп", "criticality_final": "Критичность"},
        title=title,
    )
    return fig


def sunburst_hypotheses(df, title="Sunburst: гипотезы → интерпретация → критичность"):
    fig = px.sunburst(
        df, path=["hypothesis_code", "interpretation", "criticality"],
        values="findings_count", color="criticality",
        color_discrete_map=CRITICALITY_COLORS, title=title,
    )
    return fig


def grouped_bar_hypothesis_companies(df, title="Уникальных компаний по гипотезам"):
    fig = px.bar(
        df, x="hypothesis_code", y="companies_count", color="interpretation",
        color_discrete_map=INTERPRETATION_COLORS, barmode="group",
        labels={"hypothesis_code": "Гипотеза", "companies_count": "Уникальных компаний"},
        title=title,
    )
    return fig


def boxplot_zscore(df, title="Box plot: Z-score по гипотезам"):
    df_z = df.dropna(subset=["zscore"])
    fig = px.box(
        df_z, x="hypothesis_code", y="zscore", color="interpretation",
        color_discrete_map=INTERPRETATION_COLORS,
        labels={"hypothesis_code": "Гипотеза", "zscore": "Z-score"},
        title=title,
    )
    return fig


def pie_risk_vs_signal(df, title="Доля Risk vs Economic Signal"):
    pie_data = df.groupby("interpretation")["findings_count"].sum().reset_index()
    fig = px.pie(
        pie_data, values="findings_count", names="interpretation",
        color="interpretation", color_discrete_map=INTERPRETATION_COLORS,
        hole=0.4, title=title,
    )
    fig.update_traces(textinfo="value+percent")
    return fig
