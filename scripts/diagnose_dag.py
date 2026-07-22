import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

# Check staging data
stdin, stdout, stderr = ssh.exec_command(
    "docker exec podft-postgres psql -U podft -d analytics -c \"SELECT COUNT(*) FROM staging.test_dataset\" 2>&1"
)
print('Staging rows:', stdout.read().decode(errors='replace').strip())

# Check if load_raw task log shows success
stdin2, stdout2, stderr2 = ssh.exec_command(
    'tail -10 /opt/analytics/logs/dag_id=vectornode_anomaly_etl/run_id=manual_002/task_id=load_raw/attempt=1.log 2>&1'
)
print('\nLoad_raw log tail:')
print(stdout2.read().decode(errors='replace').strip()[:500])

# Check scheduler status
stdin3, stdout3, stderr3 = ssh.exec_command('journalctl -u airflow-scheduler --no-pager -n 5 2>&1')
print('\nScheduler:')
print(stdout3.read().decode(errors='replace').strip()[:300])

ssh.close()
