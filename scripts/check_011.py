import paramiko, time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

time.sleep(45)

for tbl in ["staging.test_dataset", "analytics.company", "analytics.company_year",
            "analytics.company_features", "analytics.company_growth",
            "analytics.company_zscore", "analytics.anomaly", "analytics.group_signal"]:
    stdin, stdout, stderr = ssh.exec_command(f"docker exec podft-postgres psql -U podft -d analytics -c \"SELECT COUNT(*) FROM {tbl}\" 2>&1")
    res = stdout.read().decode(errors='replace').strip()
    cnt = 'error'
    for line in res.split('\n'):
        line = line.strip()
        if line.isdigit():
            cnt = line
            break
    print(f'{tbl:40s} {cnt}')

# Check task states
stdin2, stdout2, stderr2 = ssh.exec_command('. /opt/analytics/venv/bin/activate && AIRFLOW_HOME=/opt/analytics airflow tasks states-for-dag-run vectornode_anomaly_etl manual_011 2>&1')
print('\nTasks:')
print(stdout2.read().decode(errors='replace').strip()[:600])

ssh.close()
