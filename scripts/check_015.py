import paramiko, time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

# Check scheduler logs
stdin, stdout, stderr = ssh.exec_command('journalctl -u airflow-scheduler --no-pager -n 10 --output=short-precise 2>&1')
print('Scheduler:')
print(stdout.read().decode(errors='replace').strip()[:1000])

# Restart scheduler
ssh.exec_command('systemctl restart airflow-scheduler')
time.sleep(5)

# Re-trigger
stdin2, stdout2, stderr2 = ssh.exec_command('. /opt/analytics/venv/bin/activate && AIRFLOW_HOME=/opt/analytics airflow dags trigger -r manual_015 vectornode_anomaly_etl 2>&1')
print('Trigger:', stdout2.read().decode(errors='replace').strip()[:200])

time.sleep(25)

# Check log
cmd3 = 'tail -5 /opt/analytics/logs/dag_id=vectornode_anomaly_etl/run_id=manual_015/task_id=load_raw/attempt=1.log 2>&1'
stdin3, stdout3, stderr3 = ssh.exec_command(cmd3)
print('Error:', stdout3.read().decode(errors='replace').strip()[:500])

# Data check
for tbl in ["analytics.company", "analytics.company_year", "analytics.anomaly"]:
    stdin4, stdout4, stderr4 = ssh.exec_command(f"docker exec podft-postgres psql -U podft -d analytics -c \"SELECT COUNT(*) FROM {tbl}\" 2>&1")
    res = stdout4.read().decode(errors='replace').strip()
    for line in res.split('\n'):
        if line.strip().isdigit():
            print(f'{tbl:35s} {line.strip()}')
            break

ssh.close()
