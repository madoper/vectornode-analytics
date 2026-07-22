import paramiko, time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

time.sleep(10)

# Check DAG list
stdin, stdout, stderr = ssh.exec_command('. /opt/analytics/venv/bin/activate && AIRFLOW_HOME=/opt/analytics airflow dags list 2>&1')
print('DAGs:')
print(stdout.read().decode(errors='replace').strip()[:500])

# Check DAG runs for vectornode_anomaly_etl
stdin2, stdout2, stderr2 = ssh.exec_command('. /opt/analytics/venv/bin/activate && AIRFLOW_HOME=/opt/analytics airflow dags list-runs -d vectornode_anomaly_etl 2>&1')
print('\nDAG runs:')
print(stdout2.read().decode(errors='replace').strip()[:500])

ssh.close()
