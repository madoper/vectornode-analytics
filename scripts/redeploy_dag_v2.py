import paramiko, time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

sftp = ssh.open_sftp()
sftp.put(r'D:\project\FRS_TEST\airflow\dags\anomaly_etl.py', '/opt/analytics/dags/anomaly_etl.py')
sftp.close()
print('DAG uploaded')

# Clear and trigger
ssh.exec_command('. /opt/analytics/venv/bin/activate && AIRFLOW_HOME=/opt/analytics airflow dags clear vectornode_anomaly_etl -y 2>&1')
ssh.exec_command('. /opt/analytics/venv/bin/activate && AIRFLOW_HOME=/opt/analytics airflow dags trigger -r manual_004 vectornode_anomaly_etl 2>&1')
print('Triggered manual_004')

time.sleep(30)

# Check status
stdin, stdout, stderr = ssh.exec_command('. /opt/analytics/venv/bin/activate && AIRFLOW_HOME=/opt/analytics airflow tasks states-for-dag-run vectornode_anomaly_etl manual_004 2>&1')
print('Status:', stdout.read().decode(errors='replace').strip()[:400])

# Check data
stdin2, stdout2, stderr2 = ssh.exec_command("docker exec podft-postgres psql -U podft -d analytics -c \"SELECT COUNT(*) AS cnt FROM analytics.company\" 2>&1 | tail -3")
print('Company count:', stdout2.read().decode(errors='replace').strip())

stdin3, stdout3, stderr3 = ssh.exec_command("docker exec podft-postgres psql -U podft -d analytics -c \"SELECT COUNT(*) AS cnt FROM analytics.company_year\" 2>&1 | tail -3")
print('Company_year count:', stdout3.read().decode(errors='replace').strip())

ssh.close()
