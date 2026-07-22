CRITICALITY_COLORS = {
    "critical": "#FF4B4B",
    "high": "#FF8C00",
    "medium": "#FFD700",
    "low": "#32CD32",
    "none": "#808080",
}

CRITICALITY_ORDER = ["none", "low", "medium", "high", "critical"]

INTERPRETATION_COLORS = {
    "risk": "#FF4B4B",
    "economic_signal": "#4DA6FF",
}

HYPOTHESIS_LABELS = {
    "H1": "H1: Дивидендная аномалия",
    "H2": "H2: Аномалия роста",
    "H3": "H3: Аномалия маржи",
    "H4": "H4: Финансовое давление",
    "H5": "H5: Аномалия производительности",
    "H6": "H6: Мультифлаговая аномалия",
}

HYPOTHESIS_METRICS = {
    "H1": "Дивиденды при убытке / payout ratio",
    "H2": "Рост выручки при сокращении штата",
    "H3": "Выброс чистой маржи (z-score)",
    "H4": "Финансовое давление (FPR)",
    "H5": "Выручка на сотрудника (z-score)",
    "H6": "Комбинация флагов (≥2)",
}

REGION_ORDER = None
