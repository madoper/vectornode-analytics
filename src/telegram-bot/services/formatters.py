def fmt_currency(val) -> str:
    if val is None:
        return "—"
    if abs(val) >= 1_000_000_000:
        return f"{val / 1_000_000_000:.1f} млрд"
    if abs(val) >= 1_000_000:
        return f"{val / 1_000_000:.1f} млн"
    return f"{val:,.0f}"


def fmt_flag(val: bool, criticality: str | None = None) -> str:
    if not val:
        return "⚪"
    sym = {"high": "🔴", "medium": "🟡", "low": "⚪"}
    return sym.get(criticality, "🔴")


def company_card(data: dict) -> str:
    risk = "⚠️ RISK" if data.get("risk_flag") else "✅ Норма"
    return f"""*{data['company_name']}*
ИНН: `{data.get('inn','—')}`
Отрасль: {data.get('okved_section','—')} | Регион: {data.get('region','—')}

📊 *Финансы:*
Выручка: {fmt_currency(data.get('revenue'))}
Чистая прибыль: {fmt_currency(data.get('net_profit'))}
Сотрудников: {data.get('headcount','—')}
Маржа: {data.get('net_margin','—')}%
FPR: {data.get('financial_pressure_ratio','—')}

🚨 *Статус:* {risk}
Аномалий: {data.get('anomaly_count',0)} | Критичность: {data.get('criticality_final','—')}

🕵️ *Гипотезы:* {_flags_line(data)}"""


def _flags_line(data: dict) -> str:
    flags = []
    for h in ["h1", "h2", "h3", "h4", "h5", "h6"]:
        key = f"{h}_flag"
        crit_key = f"{h}_criticality"
        if data.get(key):
            flags.append(f"{h.upper()}:{fmt_flag(True, data.get(crit_key))}")
    return " ".join(flags) if flags else "—"


def signals_card(data: dict) -> str:
    lines = []
    for h in ["h1", "h2", "h3", "h4", "h5", "h6"]:
        flag = data.get(f"{h}_flag")
        crit = data.get(f"{h}_criticality")
        labels = {
            "h1": "H1 Дивиденды > прибыли",
            "h2": "H2 Рост выручки / спад персонала",
            "h3": "H3 Экстремальная маржа",
            "h4": "H4 Фин. давление",
            "h5": "H5 Аном. выручка/сотр",
            "h6": "H6 Комбо ≥2 гипотез",
        }
        lines.append(f"{fmt_flag(flag, crit)} {labels[h]}")
    return "*Карта сигналов H1–H6:*\n" + "\n".join(lines)


def top_risk_list(companies: list[dict]) -> str:
    lines = ["*Топ компаний по риску:*"]
    for i, c in enumerate(companies, 1):
        lines.append(
            f"{i}. {c['company_name']} ({c['inn']}) — "
            f"аномалий: {c.get('anomaly_count',0)}, "
            f"{c.get('criticality_final','—')}"
        )
    return "\n".join(lines)


def groups_list(groups: list[dict]) -> str:
    lines = ["*Топ групп риска:*"]
    for i, g in enumerate(groups, 1):
        lines.append(
            f"{i}. {g['group_key']} — "
            f"компаний: {g.get('companies_count',0)}, "
            f"аномалий: {g.get('anomaly_count',0)}, "
            f"{g.get('criticality_final','—')}"
        )
    return "\n".join(lines)


def recent_list(anomalies: list[dict]) -> str:
    lines = ["*Новые аномалии:*"]
    for a in anomalies:
        lines.append(
            f"🔹 {a['company_name']} — {a['hypothesis_code']} "
            f"({a['criticality']}): {a.get('interpretation','—')}"
        )
    return "\n".join(lines)


def compare_card(companies: list[dict]) -> str:
    lines = ["*Сравнение компаний:*"]
    for c in companies:
        lines.append(
            f"\n{c['company_name']} ({c['inn']})\n"
            f"  Выручка: {fmt_currency(c.get('revenue'))}\n"
            f"  Прибыль: {fmt_currency(c.get('net_profit'))}\n"
            f"  Маржа: {c.get('net_margin','—')}%\n"
            f"  FPR: {c.get('financial_pressure_ratio','—')}\n"
            f"  Сотрудников: {c.get('headcount','—')}\n"
            f"  Аномалий: {c.get('anomaly_count',0)}\n"
            f"  Статус: {c.get('criticality_final','—')}"
        )
    return "\n".join(lines)


def answer_text(data: dict) -> str:
    text = data.get("text", "")
    fragments = data.get("fragments", [])
    if fragments:
        text += "\n\n*Источники:*\n"
        for f in fragments[:3]:
            text += f"▸ {f.get('source','—')} (score: {f.get('score',0):.2f})\n"
    return text
