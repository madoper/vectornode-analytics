set -e
export AIRFLOW_HOME=/opt/analytics
export PATH=/opt/analytics/venv/bin:$PATH
export AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=postgresql+psycopg2://airflow_user:airflow_pass@localhost:5432/airflow_db
export AIRFLOW__CORE__EXECUTOR=SequentialExecutor
export AIRFLOW__CORE__LOAD_EXAMPLES=False
export AIRFLOW__CORE__DAGS_FOLDER=/opt/analytics/dags
export AIRFLOW__WEBSERVER__WEB_SERVER_PORT=8080
export AIRFLOW__WEBSERVER__EXPOSE_CONFIG=True
export AIRFLOW__SCHEDULER__DAG_DIR_LIST_INTERVAL=30

# Remove existing airflow.cfg if any
rm -f $AIRFLOW_HOME/airflow.cfg

# Let airflow generate default config
airflow version

# Update config via env vars already set
airflow config list --defaults > /dev/null 2>&1 || true

# Initialize metadata database
echo "Initializing Airflow DB..."
airflow db init

# Create admin user
echo "Creating admin user..."
airflow users create \
    --username admin \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@vectornode.ru \
    --password admin123 2>/dev/null || echo "User may already exist"

# Verify
echo "Checking tables..."
airflow db check

echo "Setup complete"
