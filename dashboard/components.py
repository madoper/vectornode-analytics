import streamlit as st
import pandas as pd
from config import CRIT_COLORS, HYPOTHESIS_LABELS


def kpi_card(label, value, color="#FFF"):
    style = f"background:#1E1E1E;padding:16px;border-radius:8px;border-left:4px solid {color};"
    return f'<div style="{style}"><small style="color:#AAA">{label}</small><br><span style="font-size:24px;font-weight:bold;color:#FFF">{value}</span></div>'


def fmt_currency(val):
    if pd.isna(val) or val is None:
        return "—"
    return f"{val:,.0f} ₽".replace(",", " ")


def fmt_pct(val):
    if pd.isna(val) or val is None:
        return "—"
    return f"{val:.1%}"


def fmt_z(val):
    if pd.isna(val) or val is None:
        return "—"
    return f"{val:+.1f}"


def color_table(df, crit_col="criticality", rename_cols=None):
    """Return dataframe with highlighted criticality rows."""
    def _style_row(r):
        c = r.get(crit_col, "")
        bg = CRIT_COLORS.get(c, "#333")
        return [f"background:{bg};color:#FFF" if i == crit_col or bg != "#333" else "" for i in r.index]

    styled = df.style.apply(_style_row, axis=1)
    if rename_cols:
        styled = styled.set_table_styles([{"selector": "th", "props": "color:#FFF;background:#333"}])
    return styled


def export_button(df, filename="data.csv", label="📥 Скачать CSV"):
    csv = df.to_csv(index=False).encode("utf-8-sig")
    st.download_button(label=label, data=csv, file_name=filename, mime="text/csv")


def verdict_badge(row):
    score = row.get("max_criticality_score", 0)
    signal = row.get("signal_only_flag", 0)
    if score == 4:
        return "🔴 КРИТИЧЕСКИЙ — рекомендована выездная проверка"
    elif score == 3:
        return "🟠 ВЫСОКИЙ РИСК — запросить пояснения"
    elif signal:
        return "🟢 ДОБРОСОВЕСТНЫЙ — экономически объяснимые отклонения"
    else:
        return "⚪ НЕТ ЗНАЧИМЫХ АНОМАЛИЙ"
