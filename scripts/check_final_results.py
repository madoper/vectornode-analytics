import paramiko, time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

time.sleep(30)

cmd = '. /opt/analytics/venv/bin/activate && AIRFLOW_HOME=/opt/analytics airflow tasks states-for-dag-run vectornode_anomaly_etl manual_003 2>&1'
stdin, stdout, stderr = ssh.exec_command(cmd)
print('Run status:')
print(stdout.read().decode(errors='replace').strip()[:500])

for sql in [
    "SELECT COUNT(*) AS cnt FROM analytics.company",
    "SELECT COUNT(*) AS cnt FROM analytics.company_year",
    "SELECT criticality, COUNT(*) AS cnt FROM analytics.anomaly GROUP BY criticality ORDER BY criticality",
    "SELECT interpretation, COUNT(*) AS cnt FROM analytics.anomaly GROUP BY interpretation ORDER BY interpretation",
    "SELECT COUNT(*) AS cnt FROM analytics.group_signal",
]:
    stdin2, stdout2, stderr2 = ssh.exec_command(f"docker exec podft-postgres psql -U podft -d analytics -c \"{sql}\" 2>&1 | tail -10")
    print(f'\n{sql[:60]}')
    print(stdout2.read().decode(errors='replace').strip())

ssh.close()
