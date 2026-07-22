import paramiko, time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

time.sleep(15)

# Check load_raw log
stdin, stdout, stderr = ssh.exec_command('tail -5 /opt/analytics/logs/dag_id=vectornode_anomaly_etl/run_id=manual_004/task_id=load_raw/attempt=1.log 2>&1')
print('Load_raw log:')
print(stdout.read().decode(errors='replace').strip()[:500])

# Check all task logs
stdin2, stdout2, stderr2 = ssh.exec_command("for f in /opt/analytics/logs/dag_id=vectornode_anomaly_etl/run_id=manual_004/*/attempt=1.log; do echo \"=== \$f ===\"; tail -3 \"\$f\" 2>/dev/null; done 2>&1")
print('\nAll task logs:')
print(stdout2.read().decode(errors='replace').strip()[:1000])

ssh.close()
