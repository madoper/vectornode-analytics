import paramiko, time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

time.sleep(30)

# Check DAG runs
stdin, stdout, stderr = ssh.exec_command('. /opt/analytics/venv/bin/activate && AIRFLOW_HOME=/opt/analytics airflow dags list-runs -d vectornode_anomaly_etl 2>&1 | grep -v Warning | grep -v graphviz')
print('DAG runs:')
print(stdout.read().decode(errors='replace').strip()[:500])

# Check task states via database
stdin2, stdout2, stderr2 = ssh.exec_command(
    "docker exec podft-postgres psql -U podft -d airflow_db -c \"SELECT dag_id, run_id, state, execution_date FROM dag_run ORDER BY execution_date DESC LIMIT 5\" 2>&1"
)
print('\nDB runs:')
print(stdout2.read().decode(errors='replace').strip()[:500])

# Check task instances
stdin3, stdout3, stderr3 = ssh.exec_command(
    "docker exec podft-postgres psql -U podft -d airflow_db -c \"SELECT task_id, state FROM task_instance WHERE dag_id='vectornode_anomaly_etl' ORDER BY start_date DESC LIMIT 10\" 2>&1"
)
print('\nTasks:')
print(stdout3.read().decode(errors='replace').strip()[:500])

ssh.close()
