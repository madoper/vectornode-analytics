import os
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonVirtualenvOperator

default_args = {
    'owner': 'admin',
    'depends_on_past': False,
    'email_on_failure': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'analytics_pipeline',
    default_args=default_args,
    description='ML Anomaly Detection + dbt Transformations',
    schedule='0 6 * * 1',
    start_date=datetime(2025, 1, 1),
    catchup=False,
    tags=['analytics', 'ml'],
) as dag:

    run_ml = BashOperator(
        task_id='run_ml_anomaly_detection',
        bash_command=(
            'cd /opt/analytics && '
            '. venv/bin/activate && '
            'python scripts/ml_anomaly_detection.py'
        ),
    )

    run_dbt = BashOperator(
        task_id='run_dbt_transformations',
        bash_command=(
            'cd /opt/analytics/analytics_dbt && '
            '. /opt/analytics/venv/bin/activate && '
            'dbt run --profiles-dir . --project-dir .'
        ),
    )

    run_ml >> run_dbt
