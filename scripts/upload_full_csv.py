import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=30)

sftp = ssh.open_sftp()
sftp.put(r'D:\project\FRS_TEST\data\test_dataset.csv', '/opt/analytics/data/test_dataset.csv')
sftp.close()
print('CSV uploaded')

# Clear old DAG runs
ssh.exec_command('. /opt/analytics/venv/bin/activate && AIRFLOW_HOME=/opt/analytics airflow dags clear vectornode_anomaly_etl -y 2>&1')
print('DAG cleared')

# Trigger new run
stdin, stdout, stderr = ssh.exec_command('. /opt/analytics/venv/bin/activate && AIRFLOW_HOME=/opt/analytics airflow dags trigger -r manual_002 vectornode_anomaly_etl 2>&1')
print('Triggered:', stdout.read().decode(errors='replace').strip()[:200])

ssh.close()
