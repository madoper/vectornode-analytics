import paramiko, time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

sftp = ssh.open_sftp()
sftp.put(r'D:\project\FRS_TEST\airflow\dags\anomaly_etl.py', '/opt/analytics/dags/anomaly_etl.py')
sftp.close()
print('DAG uploaded')

# Restart scheduler
ssh.exec_command('systemctl restart airflow-scheduler')
time.sleep(5)

# Trigger
stdin, stdout, stderr = ssh.exec_command('. /opt/analytics/venv/bin/activate && AIRFLOW_HOME=/opt/analytics airflow dags trigger -r manual_006 vectornode_anomaly_etl 2>&1')
print('Trigger:', stdout.read().decode(errors='replace').strip()[:200])

ssh.close()
