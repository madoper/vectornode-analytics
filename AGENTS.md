# AGENTS.md — VectorNode Analytics

## Project overview

Anomaly-detection and economic-signal platform for Russian company financial data (2023–2025).
Pipeline: CSV → feature engineering → robust z-score → anomaly hypotheses (H1–H6) → group signals → dashboards.

**Core technologies:** Apache Airflow 2.10.5, PostgreSQL (via `podft-postgres` Docker container), dbt, Streamlit, Nginx reverse proxy.
All Python. No JS/TS, no Node, no Dockerfiles in this repo.

## Directory boundaries

| Directory | Role |
|---|---|
| `dags/` | Simple Airflow DAG (2 tasks: ML → dbt), **scheduled weekly Mon 6 AM** |
| `airflow/` | `requirements.txt` for Airflow venv |
| `dashboard/` | Streamlit app (5 tabs), served on `:8501` |
| `dbt/` | dbt project (`analytics_dbt`): staging views + marts tables |
| `data/` | CSV datasets (input `test_dataset.csv` + exported results) |
| `scripts/` | ~440 operational scripts (deploy, debug, check, verify). **Not tests** — ad-hoc manual tooling. |
| `nginx/` | Nginx config fragments (reverse proxy + SSL) |
| `systemd/` | Airflow webserver + scheduler unit files |
| `vectornode-analytics/` | **Separate nested git repo** with its own CI, full 10-task ETL DAG, and README |

## Architecture notes (non-obvious)

- **Two Airflow DAGs exist:**
  - `dags/analytics_dag.py` — simple weekly pipeline (ML script → dbt run)
  - `vectornode-analytics/airflow/dags/anomaly_etl.py` — full 10-task pipeline (manual trigger only)
- **Two separate deployments** on the VPS: `/opt/analytics` (root code) and `/opt/vectornode-analytics` (nested sub-repo). Each has its own GitHub Actions deploy workflow.
- **Pandas 3.x + SQLAlchemy workaround:** some ETL code uses `raw_connection()` + `pd.read_sql()` to bypass a `pandas>=3` incompatibility with `SQLAlchemy<2`.
- **Robust z-score:** median + MAD with 1.4826 consistency constant, fallback to std-dev if MAD == 0.
- **6 anomaly hypotheses:** H1 (dividends), H2 (rev growth + headcount drop), H3 (net margin outliers), H4 (financial pressure), H5 (rev-per-emp outliers), H6 (multi-flag combos ≥2).
- **All UI labels and report text are in Russian.**
- **No formal build, test, lint, or typecheck tooling.** No `Makefile`, `pyproject.toml`, `pytest`, `tox`, or pre-commit hooks.

## Database

Single PostgreSQL instance (`podft-postgres` container, port 5432):
- Database `analytics` — main data (schemas: `analytics`, `staging`, `marts`, `reporting`)
- Database `airflow_db` — Airflow metadata
- DDL: `scripts/ddl.sql` (creates analytics schema, tables, indexes, dashboard view)
- Dashboard reads from `reporting.*` views/tables via `postgresql+psycopg2://podft:podft-secret@localhost:5432/analytics`

## Developer commands

```bash
# Install Airflow (creates /opt/analytics/venv)
bash install_airflow.sh

# Init Airflow DB + create admin user
bash scripts/airflow_db_setup.sh

# Run DDL to create analytics tables
docker exec -i podft-postgres psql -U podft -d analytics < scripts/ddl.sql

# Run ML pipeline standalone
python scripts/run_ml.py

# Run dbt
cd dbt
dbt run --profiles-dir . --project-dir .

# Run Streamlit dashboard
cd dashboard
streamlit run app.py --server.port 8501

# Start services on VPS
systemctl start airflow-webserver airflow-scheduler
docker start podft-postgres podft-superset
```

## Deploy

Push to `main` → GitHub Actions (`appleboy/ssh-action@v1.0.3`) SSHes to VPS:
1. `cd /opt/analytics && git pull origin main`
2. `cp -r airflow/dags/* dags/`
3. `systemctl restart airflow-scheduler airflow-webserver`

Secrets required: `VPS_HOST`, `VPS_USER`, `VPS_SSH_KEY`.

## Environment & constraints

- **Production paths are hardcoded** to `/opt/analytics` in DAGs, scripts, and systemd units.
- **No container build step** — `podft-postgres` and `podft-superset` Docker containers are managed outside this repo.
- Python packages defined only in `airflow/requirements.txt` (pandas 3.0.3, numpy 1.26.4, sqlalchemy 1.4.54, psycopg2-binary 2.9.10). No root-level requirements file.
- dbt profile (`dbt/profiles.yml`) expects PostgreSQL on `localhost:5432`, user `dbt_user`, database `analytics`.
