# VectorNode Analytics

Аналитическая платформа для поиска аномалий и экономических сигналов.

## Архитектура

- **Airflow** — оркестрация ETL (systemd, порт 8081)
- **Superset** — BI-дашборды (podft-superset, порт 8088)
- **PostgreSQL** — метаданные + аналитика (podft-postgres)

## Домены

| Субдомен | Сервис |
|---|---|
| `admin.vectornode.ru` | Airflow UI |
| `bi.vectornode.ru` | Superset BI |
| `vectornode.ru` | PodFT + Superset (legacy) |

## DAG: vectornode_anomaly_etl

1. `load_raw` — загрузка и валидация CSV
2. `build_features` — расчёт 12 производных признаков
3. `build_zscore` — robust z-score по отраслям
4. `detect_anomalies` — 7 гипотез + интерпретация
5. `build_group_signals` — групповые сигналы

## Деплой

Push в `main` → GitHub Actions → автодеплой на VPS.
