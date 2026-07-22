import plotly.express as px
import plotly.graph_objects as go
from .constants import CRITICALITY_COLORS, CRITICALITY_ORDER, INTERPRETATION_COLORS, HYPOTHESIS_LABELS

def format_rub(v):
    if abs(v) >= 1_000_000:
        return f"{v/1_000_000:,.1f} млн"
    return f"{v:,.0f}"

def kpi_card(label, value, delta=None, color="#FFFFFF"):
    card_style = f"background:#1E1E1E;padding:16px;border-radius:8px;border-left:4px solid {color};margin:4px;"
    html = f'<div style="{card_style}"><small style="color:#AAA">{label}</small><br>'
    html += f'<span style="font-size:24px;font-weight:bold;color:#FFF">{value}</span>'
    if delta:
        html += f'<br><small style="color:#AAA">{delta}</small>'
    html += '</div>'
    return html

def criticality_bar(df, col, title, x_label, y_label):
    cat_order = [c for c in CRITICALITY_ORDER if c in df[col].values]
    counts = df[col].value_counts().reindex(cat_order, fill_value=0)
    fig = px.bar(x=counts.index, y=counts.values, color=counts.index,
                  color_discrete_map=CRITICALITY_COLORS, title=title)
    fig.update_xaxes(title=x_label)
    fig.update_yaxes(title=y_label)
    fig.update_layout(showlegend=False)
    return fig

def hypothesis_bar(df, x_col, y_col, color_col, title):
    df = df.copy()
    df[x_col] = df[x_col].map(lambda h: HYPOTHESIS_LABELS.get(h, h))
    fig = px.bar(df, x=x_col, y=y_col, color=color_col,
                 color_discrete_map=INTERPRETATION_COLORS, title=title,
                 barmode="stack" if color_col else "group")
    return fig

def hypothesis_heatmap(df, row_col, col_col, val_col, title):
    pivot = df.pivot_table(values=val_col, index=row_col, columns=col_col, aggfunc="sum", fill_value=0)
    fig = px.imshow(pivot, text_auto=True, aspect="auto", title=title,
                    color_continuous_scale="Reds")
    return fig

def scatter_zscore(df, title):
    fig = px.scatter(df, x="zscore", y="criticality_score", color="hypothesis_code",
                     size=df["value"].abs().clip(upper=df["value"].abs().quantile(0.95)),
                     hover_data=["company_name", "year", "metric", "interpretation_reason"],
                     title=title)
    return fig

def line_chart(df, x, y_cols, title):
    fig = go.Figure()
    for col, name in y_cols:
        fig.add_trace(go.Scatter(x=df[x], y=df[col], name=name, mode="lines+markers"))
    fig.update_layout(title=title, hovermode="x")
    return fig

def radar_zscores(row, title):
    cats = ["net_margin_z", "rev_per_emp_z", "financial_pressure_z", "rev_growth_z", "emp_growth_z"]
    labels = ["Маржа", "Выручка/сотр", "Фин. давление", "Рост выручки", "Рост числ-ти"]
    values = [row.get(c, 0) or 0 for c in cats]
    fig = go.Figure(go.Scatterpolar(r=values, theta=labels, fill="toself", name="Z-score"))
    fig.update_layout(title=title, polar=dict(radialaxis=dict(visible=True, range=[-4, 4])))
    return fig
