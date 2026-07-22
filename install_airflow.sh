#!/bin/bash
set -e
python3 -m venv /opt/analytics/venv
source /opt/analytics/venv/bin/activate
pip install --upgrade pip setuptools wheel -q

AIRFLOW_VERSION=2.10.5
PYTHON_VERSION=$(python3 -c "import sys; print(f\"{sys.version_info.major}.{sys.version_info.minor}\")")
CONSTRAINT_URL="https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-${PYTHON_VERSION}.txt"

pip install "apache-airflow[postgres]==${AIRFLOW_VERSION}" --constraint "${CONSTRAINT_URL}" -q
echo "Airflow installed successfully"
