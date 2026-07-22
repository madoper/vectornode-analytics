# VectorNode Analytics

Аналитическая платформа для поиска аномалий и экономических сигналов.

## Архитектура

- **Airflow** — оркестрация ETL (systemd, порт 8081)
- **Streamlit** — кастомные BI-дашборды 
- **PostgreSQL** — метаданные + аналитика (podft-postgres)

## Домены

| Субдомен | Сервис |
|---|---|
| `admin.vectornode.ru` | Airflow UI |
| `analytics.vectornode.ru` | BI |
| `vectornode.ru` | PodFT (legacy) |

## DAG: vectornode_anomaly_etl

1. `load_raw` — загрузка и валидация CSV
2. `build_features` — расчёт 12 производных признаков
3. `build_zscore` — robust z-score по отраслям
4. `detect_anomalies` — 6 гипотез + интерпретация
5. `build_group_signals` — групповые сигналы

## Деплой

Push в `main` → GitHub Actions → автодеплой на VPS.
