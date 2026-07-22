import paramiko, time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

time.sleep(30)

# Check error in log
cmd = 'tail -5 /opt/analytics/logs/dag_id=vectornode_anomaly_etl/run_id=manual_013/task_id=load_raw/attempt=1.log 2>&1'
stdin, stdout, stderr = ssh.exec_command(cmd)
print('Error:', stdout.read().decode(errors='replace').strip()[:500])

# Check data
for tbl in ["staging.test_dataset", "analytics.company", "analytics.company_year",
            "analytics.anomaly"]:
    stdin2, stdout2, stderr2 = ssh.exec_command(f"docker exec podft-postgres psql -U podft -d analytics -c \"SELECT COUNT(*) FROM {tbl}\" 2>&1")
    res = stdout2.read().decode(errors='replace').strip()
    for line in res.split('\n'):
        line = line.strip()
        if line.isdigit():
            print(f'{tbl:35s} {line}')
            break

ssh.close()
