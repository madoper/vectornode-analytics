import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import text
from db import engine, DB_URL
from queries import *
from config import *
from components import *

st.set_page_config(page_title="ФНС Аналитика", page_icon="static/logo.svg", layout="wide", initial_sidebar_state="expanded")

if "cleared" not in st.session_state:
    st.cache_data.clear()
    st.cache_resource.clear()
    st.session_state["cleared"] = True

st.markdown("""<link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">""", unsafe_allow_html=True)

try:
    with engine.connect() as c:
        c.execute(text("SELECT 1"))
except Exception as e:
    st.error(f"Нет подключения к БД: {e}")
    st.stop()

pages = {"▤ Обзор": 0, "◎ Компания": 1, "⚗ Гипотезы": 2, "⊞ Группы": 3, "⬡ Отрасли": 4, "📋 Методика": 5, "📊 Процесс анализа": 6}
sel = st.sidebar.radio("Дашборд", list(pages.keys()), key="nav_radio")
st.sidebar.markdown("---")
st.sidebar.caption("ФНС Аналитика — риск-мониторинг")

page = pages[sel]

# ======================== PAGE 0: OVERVIEW ========================
if page == 0:
    st.markdown("## <i class='material-icons'>bar_chart</i> Обзор", unsafe_allow_html=True)
    with engine.connect() as conn:
        kpi = conn.execute(text(Q_KPI)).fetchone()

    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown(kpi_card("Компаний в анализе", kpi[0], "#4DA6FF"), unsafe_allow_html=True)
    with c2: st.markdown(kpi_card("Критических аномалий", kpi[1], "#ff4b4b"), unsafe_allow_html=True)
    with c3: st.markdown(kpi_card("Risk-компаний", kpi[2], "#ff9f43"), unsafe_allow_html=True)
    with c4: st.markdown(kpi_card("Период", kpi[3], "#2ed573"), unsafe_allow_html=True)

    with st.expander("Итоговое резюме", expanded=True):
        st.markdown(RESUME_TEXT)
        st.markdown("#### Расшифровка ключевых маркеров")
        mk = pd.DataFrame(KEY_COMPANIES)
        st.dataframe(mk, column_config={"company_id": "ID", "name": "Компания", "marker": "Маркер", "basis": "Основание", "priority": "Приоритет"}, use_container_width=True, hide_index=True)
        export_button(mk, "key_companies.csv")

    with engine.connect() as conn:
        h1 = conn.execute(text(Q_PRIORITY_H1)).fetchall()
        h5 = conn.execute(text(Q_PRIORITY_H5_TRANSIT)).fetchall()
        h4 = conn.execute(text(Q_PRIORITY_H4_LOSS)).fetchall()
        h3 = conn.execute(text(Q_PRIORITY_H3_LOW_MARGIN)).fetchall()
        good = conn.execute(text(Q_GOOD_COMPANIES)).fetchall()

    def card(col, title, color, items, fields):
        with col:
            h = f'<div style="border:2px solid {color};border-radius:8px;padding:8px;height:380px;overflow-y:auto"><h5 style="color:{color}">{title}</h5>'
            for it in items:
                n = getattr(it, "company_name", "") or it[1]
                h += f"<b>{n}</b><br>"
                for i, f in enumerate(fields):
                    v = getattr(it, f, None) or (it[i + 2] if len(it) > i + 2 else "")
                    h += f"<small>{f}: {v}</small><br>"
                h += "<hr>"
            h += "</div>"
            st.markdown(h, unsafe_allow_html=True)

    c1, c2, c3, c4, c5 = st.columns(5)
    card(c1, "Вывод средств H1", "#ff4b4b", h1, ["dividends_paid", "net_profit"])
    card(c2, "Транзит H5", "#ff9f43", h5, ["revenue", "zscore"])
    card(c3, "Убытки+давление H4", "#feca57", h4, ["fpr", "net_profit"])
    card(c4, "Низкая маржа H3", "#a855f7", h3, ["net_margin", "zscore"])
    card(c5, "Добросовестные", "#2ed573", good, ["top_hypothesis_code", "top_reason"])

    with engine.connect() as conn:
        hs = pd.read_sql(text(Q_HYPOTHESIS_SUMMARY), conn)

    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(px.bar(hs, x="hypothesis_code", y="findings_count", color="criticality", color_discrete_map=CRIT_COLORS, barmode="stack",
            labels={"hypothesis_code": "Гипотеза", "findings_count": "Находок", "criticality": "Критичность"}), use_container_width=True)
    with c2:
        st.plotly_chart(px.treemap(hs, path=["hypothesis_code"], values="findings_count", color="criticality", color_discrete_map=CRIT_COLORS,
            labels={"hypothesis_code": "Гипотеза", "findings_count": "Находок"}), use_container_width=True)

    st.markdown("**Рекомендации:** 1) Выездные проверки: C0254, C0069, C0008, C0288. 2) Сверка: C0473, C0385. 3) Пояснения: C0380, C0308. 4) Анализ групп founder_id.")

# ======================== PAGE 1: COMPANY ========================
elif page == 1:
    st.markdown("## <i class='material-icons'>business</i> Профиль компании", unsafe_allow_html=True)
    with engine.connect() as conn:
        companies = conn.execute(text(Q_ALL_COMPANIES)).fetchall()
    opts = {f"{c.company_id} — {c.company_name}": c.company_id for c in companies}
    idx = 0
    if "selected_company" in st.session_state:
        for i, (l, cid) in enumerate(opts.items()):
            if cid == st.session_state["selected_company"]:
                idx = i; break
        del st.session_state["selected_company"]
    sel = st.selectbox("Компания", list(opts.keys()), index=idx)
    cid = opts[sel]

    with engine.connect() as conn:
        tl = pd.read_sql(text(Q_COMPANY_TIMELINE), conn, params={"cid": cid})
        an = pd.read_sql(text(Q_COMPANY_ANOMALIES), conn, params={"cid": cid})
        fl = pd.read_sql(text(Q_COMPANY_FLAGS), conn, params={"cid": cid})
    if tl.empty:
        st.warning("Нет данных"); st.stop()
    last = tl.iloc[-1]

    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown(kpi_card("Выручка", fmt_currency(last["revenue"]), "#4DA6FF"), unsafe_allow_html=True)
    with c2: st.markdown(kpi_card("Прибыль", fmt_currency(last["net_profit"]), "#2ed573" if last["net_profit"] and last["net_profit"] > 0 else "#ff4b4b"), unsafe_allow_html=True)
    with c3: st.markdown(kpi_card("Маржа", fmt_pct(last["net_margin"]), "#feca57"), unsafe_allow_html=True)
    with c4: st.markdown(kpi_card("Штат", str(int(last["headcount"])) if last["headcount"] else "—"), unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown(kpi_card("tax_to_profit", fmt_pct(last["tax_to_profit"]), "#4DA6FF"), unsafe_allow_html=True)
    with c2: st.markdown(kpi_card("FPR", f"{last['fpr']:.2f}" if last["fpr"] else "—", "#ff9f43"), unsafe_allow_html=True)
    with c3: st.markdown(kpi_card("Аномалий", str(int(last["anomaly_count"]))), unsafe_allow_html=True)
    with c4:
        badge = verdict_badge(last)
        clr = "#ff4b4b" if "КРИТИЧЕСКИЙ" in badge else "#ff9f43" if "ВЫСОКИЙ" in badge else "#2ed573"
        st.markdown(kpi_card("Статус", badge.split("—")[0].strip(), clr), unsafe_allow_html=True)
    st.markdown(f'<div style="padding:8px;background:#333;border-radius:8px;color:#FFF">{badge}</div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        fig = go.Figure()
        fig.add_trace(go.Bar(x=tl["year"], y=tl["revenue"] / 1_000_000, name="Выручка (млн)", marker_color="#4DA6FF"))
        fig.add_trace(go.Scatter(x=tl["year"], y=tl["net_profit"] / 1_000_000, name="Прибыль (млн)", mode="lines+markers", line=dict(color="#2ed573", width=3)))
        fig.update_layout(title="Выручка и прибыль")
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=tl["year"], y=tl["net_margin"] * 100, name="Маржа %", mode="lines+markers", line=dict(color="#4DA6FF", width=3)))
        fig.add_trace(go.Scatter(x=tl["year"], y=tl["tax_to_profit"], name="Налог/прибыль", mode="lines+markers", line=dict(color="#ff9f43", width=2), yaxis="y2"))
        fig.update_layout(title="Маржа и налоги", yaxis2=dict(overlaying="y", side="right"))
        st.plotly_chart(fig, use_container_width=True)

    fig = go.Figure()
    fig.add_trace(go.Bar(x=tl["year"], y=tl["headcount"], name="Штат", marker_color="#feca57"))
    if tl["revenue"].sum() > 0:
        fig.add_trace(go.Scatter(x=tl["year"], y=tl["revenue"] / tl["headcount"].clip(lower=1), name="Выручка/сотр", mode="lines+markers", line=dict(color="#4DA6FF", width=2), yaxis="y2"))
        fig.update_layout(yaxis2=dict(overlaying="y", side="right"))
    fig.update_layout(title="Штат и производительность")
    st.plotly_chart(fig, use_container_width=True)

    if not an.empty:
        st.markdown("#### Аномалии")
        an_disp = an.rename(columns={
            "year": "Год", "hypothesis_code": "Гипотеза", "metric": "Метрика",
            "value": "Значение", "zscore": "Z-score", "interpretation": "Тип",
            "interpretation_reason": "Причина", "criticality": "Критичность", "criticality_score": "Балл"
        })
        st.dataframe(an_disp.style.apply(lambda r: [f"background:{CRIT_COLORS.get(r['Критичность'],'')};color:#FFF" if r['Критичность'] in CRIT_COLORS else "" for _ in r.index], axis=1), use_container_width=True, hide_index=True)
        export_button(an, f"{cid}_anomalies.csv")
    if not fl.empty:
        st.markdown("#### Флаги H1–H6")
        hm = fl.set_index("year")[[f"h{i}_flag" for i in range(1, 7)]]
        hm.columns = [f"H{i}" for i in range(1, 7)]
        st.plotly_chart(px.imshow(hm.T, text_auto=True, aspect="auto", color_continuous_scale="RdYlGn"), use_container_width=True)

# ======================== PAGE 2: HYPOTHESES ========================
elif page == 2:
    st.markdown("## <i class='material-icons'>science</i> Анализ гипотез", unsafe_allow_html=True)
    with engine.connect() as conn:
        hs = pd.read_sql(text(Q_HYPOTHESIS_SUMMARY), conn)
    hs_disp = hs.rename(columns={
        "hypothesis_code": "Гипотеза", "interpretation": "Тип", "criticality": "Критичность",
        "findings_count": "Находок", "companies_count": "Компаний", "company_year_count": "Компаний×год"
    })
    st.dataframe(hs_disp.style.apply(lambda r: [f"background:{CRIT_COLORS.get(r['Критичность'],'')}" if r['Критичность'] in CRIT_COLORS else "" for _ in r.index], axis=1), use_container_width=True, hide_index=True)
    export_button(hs, "hypothesis_summary.csv")

    hyps = sorted(hs["hypothesis_code"].unique())
    h = st.selectbox("Гипотеза", hyps, format_func=lambda x: HYPOTHESIS_LABELS.get(x, x))
    with engine.connect() as conn:
        yrs = [r[0] for r in conn.execute(text(Q_HYPOTHESIS_YEARS)).fetchall()]
    y = st.selectbox("Год", ["Все"] + [str(y) for y in yrs])

    with engine.connect() as conn:
        sc = pd.read_sql(text(Q_ANOMALY_SCATTER), conn, params={"h": h, "y": None if y == "Все" else int(y)})
    sc_z = sc.dropna(subset=["zscore"]).copy()
    if not sc_z.empty:
        sc_z["size_val"] = sc_z["net_profit"].fillna(0).abs().clip(upper=sc_z["net_profit"].fillna(0).abs().quantile(0.95))
        fig = px.scatter(sc_z, x="value", y="zscore", color="criticality", size="size_val",
                         hover_data=["company_name", "year", "interpretation"],
                         color_discrete_map=CRIT_COLORS,
                         labels={"value": "Значение", "zscore": "Z‑score", "criticality": "Критичность"})
        fig.add_hline(y=2, line_dash="dash", line_color="#feca57")
        fig.add_hline(y=-2, line_dash="dash", line_color="#feca57")
        fig.add_hline(y=3, line_dash="dash", line_color="#ff4b4b")
        fig.add_hline(y=-3, line_dash="dash", line_color="#ff4b4b")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Нет данных с z-score для выбранной гипотезы")
    if not sc.empty:
        disp = sc.dropna(subset=["zscore"])
        if not disp.empty:
            disp = disp.sort_values("zscore", key=lambda x: x.abs(), ascending=False)
            disp_disp = disp.rename(columns={
                "company_id": "ID", "company_name": "Компания", "year": "Год",
                "value": "Значение", "zscore": "Z‑score", "criticality": "Критичность",
                "interpretation": "Тип", "net_profit": "Прибыль", "headcount": "Штат"
            })
            st.dataframe(disp_disp, use_container_width=True, hide_index=True)
            if st.button("Перейти к компании"):
                st.session_state["selected_company"] = disp.iloc[0]["company_id"]
                st.rerun()

# ======================== PAGE 3: GROUPS ========================
elif page == 3:
    st.markdown("## <i class='material-icons'>groups</i> Групповой анализ", unsafe_allow_html=True)
    gtype = st.radio("Тип группы", ["founder", "address"], horizontal=True)
    with engine.connect() as conn:
        grp = pd.read_sql(text(Q_GROUPS), conn, params={"gtype": gtype})
    if grp.empty:
        st.info("Нет данных"); st.stop()
    multi_only = st.checkbox("Только группы ≥ 2 компаний", value=True)
    if multi_only:
        grp = grp[grp["companies_count"] >= 2]
    if grp.empty:
        st.info("Нет групп с ≥ 2 компаниями"); st.stop()
    grp_disp = grp.rename(columns={
        "group_key": "Группа", "companies_count": "Компаний",
        "risk_anomaly_count": "Риск. аномалии", "signal_anomaly_count": "Сигн. аномалии",
        "anomaly_count": "Аномалий", "avg_criticality_score": "Ср. балл",
        "max_criticality_score": "Макс. балл", "criticality_final": "Критичность",
        "interpretation_final": "Тип"
    })
    st.dataframe(grp_disp.style.apply(lambda r: [f"background:{CRIT_COLORS.get(r['Критичность'],'')};color:#FFF" if r['Критичность'] in CRIT_COLORS else "" for _ in r.index], axis=1), use_container_width=True, hide_index=True)
    export_button(grp, f"groups_{gtype}.csv")
    top = grp.nlargest(20, "anomaly_count")
    fig = px.bar(top, x="anomaly_count", y="group_key", orientation="h", color="max_criticality_score", color_continuous_scale="Reds")
    fig.update_layout(yaxis_categoryorder="total ascending")
    st.plotly_chart(fig, use_container_width=True)
    sel = st.selectbox("Детализация", grp["group_key"])
    det = grp[grp["group_key"] == sel]
    if not det.empty:
        det_disp = det.rename(columns={
            "group_key": "Группа", "companies_count": "Компаний",
            "risk_anomaly_count": "Риск. аномалии", "signal_anomaly_count": "Сигн. аномалии",
            "anomaly_count": "Аномалий", "avg_criticality_score": "Ср. балл",
            "max_criticality_score": "Макс. балл", "criticality_final": "Критичность",
            "interpretation_final": "Тип"
        })
        st.dataframe(det_disp, use_container_width=True, hide_index=True)

# ======================== PAGE 4: INDUSTRY ========================
elif page == 4:
    st.markdown("## <i class='material-icons'>business</i> Отраслевой анализ", unsafe_allow_html=True)

    with engine.connect() as conn:
        ind_margin = pd.read_sql(text(Q_INDUSTRY_MARGIN), conn)
        ind_tax = pd.read_sql(text(Q_INDUSTRY_TAX), conn)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### Boxplot: маржа по отраслям")
        fig1 = go.Figure()
        outlier_x = []; outlier_y = []; outlier_text = []
        for sector in sorted(ind_margin["okved_section"].dropna().unique()):
            vals = ind_margin[ind_margin["okved_section"] == sector]["net_margin"].dropna()
            q1, q3 = vals.quantile(0.25), vals.quantile(0.75)
            iqr = q3 - q1
            lo, hi = q1 - 1.5 * iqr, q3 + 1.5 * iqr
            out = ind_margin[(ind_margin["okved_section"] == sector) & ((ind_margin["net_margin"] < lo) | (ind_margin["net_margin"] > hi))]
            for _, r in out.iterrows():
                outlier_x.append(sector)
                outlier_y.append(r["net_margin"])
                outlier_text.append(f"{r['company_name']}<br>Маржа: {r['net_margin']:.1%}")
            fig1.add_trace(go.Box(y=vals, name=sector, showlegend=False, marker_color="#4DA6FF"))
        fig1.add_trace(go.Scatter(x=outlier_x, y=outlier_y, mode="markers",
                                   marker=dict(color="#ff4b4b", size=8, symbol="x"),
                                   text=outlier_text, hovertemplate="%{text}<extra></extra>",
                                   name="Выбросы"))
        fig1.update_xaxes(tickangle=45, title="Отрасль")
        fig1.update_yaxes(title="Чистая маржа")
        st.plotly_chart(fig1, use_container_width=True)

    with c2:
        st.markdown("#### Среднее фин. давление по отраслям")
        fig2 = px.bar(ind_tax, x="okved_section", y="avg_fpr",
                       color="avg_fpr", color_continuous_scale="Reds",
                       labels={"okved_section": "Отрасль", "avg_fpr": "Средний FPR"})
        fig2.update_xaxes(tickangle=45)
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("#### Средняя налоговая нагрузка по отраслям")
    fig3 = px.bar(ind_tax, x="okved_section", y="avg_tax_to_profit",
                   color="avg_tax_to_profit", color_continuous_scale="Blues",
                   labels={"okved_section": "Отрасль", "avg_tax_to_profit": "Средний tax/profit"})
    fig3.update_xaxes(tickangle=45)
    st.plotly_chart(fig3, use_container_width=True)

# ======================== PAGE 5: METHODOLOGY ========================
elif page == 5:
    st.markdown(open("methodology.md", encoding="utf-8").read())

# ======================== PAGE 6: ANALYSIS PROCESS ========================
elif page == 6:
    st.image("FRS1.jpeg", use_container_width=True)
