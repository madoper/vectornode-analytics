import paramiko, time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=30)

# Upload the full CSV
sftp = ssh.open_sftp()
sftp.put(r'D:\project\FRS_TEST\data\test_dataset.csv', '/opt/analytics/data/test_dataset.csv')
sftp.close()
print('CSV uploaded')

# Check size
stdin, stdout, stderr = ssh.exec_command('wc -l /opt/analytics/data/test_dataset.csv')
print('Lines:', stdout.read().decode(errors='replace').strip())

# Trigger new DAG run
ssh.exec_command('. /opt/analytics/venv/bin/activate && AIRFLOW_HOME=/opt/analytics airflow dags trigger -r full_data_001 vectornode_anomaly_etl 2>&1')
print('DAG triggered')

time.sleep(60)

# Check results
for sql in [
    "SELECT COUNT(*) FROM analytics.company",
    "SELECT COUNT(*) FROM analytics.company_year",
    "SELECT criticality, COUNT(*) FROM analytics.anomaly GROUP BY criticality ORDER BY criticality",
    "SELECT interpretation, COUNT(*) FROM analytics.anomaly GROUP BY interpretation",
    "SELECT hypothesis_code, COUNT(*) FROM analytics.anomaly GROUP BY hypothesis_code",
]:
    stdin2, stdout2, stderr2 = ssh.exec_command(f"docker exec podft-postgres psql -U podft -d analytics -c \"{sql}\" 2>&1 | tail -10")
    print(stdout2.read().decode(errors='replace').strip())
    print()

ssh.close()
