import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

# Check DAG details
cmd = '. /opt/analytics/venv/bin/activate && AIRFLOW_HOME=/opt/analytics airflow dags details vectornode_anomaly_etl 2>&1 | grep -E "is_paused|dag_id|fileloc|schedule"'
stdin, stdout, stderr = ssh.exec_command(cmd)
print('DAG details:')
print(stdout.read().decode(errors='replace').strip())

# Check if the DAG file parses correctly
cmd2 = '. /opt/analytics/venv/bin/activate && python -c "import sys; sys.path.insert(0,\"/opt/analytics/dags\"); from anomaly_etl import dag; print(dag.dag_id)" 2>&1'
stdin2, stdout2, stderr2 = ssh.exec_command(cmd2)
print('\nDAG parse:', stdout2.read().decode(errors='replace').strip()[:200])

# Re-trigger
cmd3 = '. /opt/analytics/venv/bin/activate && AIRFLOW_HOME=/opt/analytics airflow dags trigger -r manual_013 vectornode_anomaly_etl 2>&1'
stdin3, stdout3, stderr3 = ssh.exec_command(cmd3)
print('\nTrigger:', stdout3.read().decode(errors='replace').strip()[:200])

ssh.close()
