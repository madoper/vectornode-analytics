CRITICALITY_COLORS = {
    "critical": "#FF4B4B",
    "high": "#FF8C00",
    "medium": "#FFD700",
    "low": "#32CD32",
    "none": "#808080",
}

CRITICALITY_ORDER = ["none", "low", "medium", "high", "critical"]

CRITICALITY_SCORE_MAP = {"none": 0, "low": 1, "medium": 2, "high": 3, "critical": 4}

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
