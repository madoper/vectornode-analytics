import paramiko, time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

time.sleep(30)

# Check run status
cmd = ('. /opt/analytics/venv/bin/activate && AIRFLOW_HOME=/opt/analytics '
       'airflow tasks states-for-dag-run vectornode_anomaly_etl manual_005 2>&1')
stdin, stdout, stderr = ssh.exec_command(cmd)
out = stdout.read().decode(errors='replace').strip()
print('Tasks:')
print(out[:500])

# Check data
for sql in [
    "SELECT COUNT(*) FROM analytics.company",
    "SELECT COUNT(*) FROM analytics.company_features",
    "SELECT COUNT(*) FROM analytics.company_zscore",
    "SELECT criticality, COUNT(*) FROM analytics.anomaly GROUP BY criticality ORDER BY criticality",
    "SELECT interpretation, COUNT(*) FROM analytics.anomaly GROUP BY interpretation ORDER BY interpretation",
]:
    stdin2, stdout2, stderr2 = ssh.exec_command(f"docker exec podft-postgres psql -U podft -d analytics -c \"{sql}\" 2>&1 | tail -10")
    print(f'\n{sql.split("FROM")[0].strip()}'.ljust(30), stdout2.read().decode(errors='replace').strip())

ssh.close()
