import paramiko, time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

time.sleep(25)

# Check error
cmd = "grep -A5 'CREATE TABLE failed' /opt/analytics/logs/dag_id=vectornode_anomaly_etl/run_id=manual_009/task_id=load_raw/attempt=1.log"
stdin, stdout, stderr = ssh.exec_command(cmd)
print('CREATE TABLE error:')
print(stdout.read().decode(errors='replace').strip()[:500])

# Also check for trailing error
cmd2 = 'tail -10 /opt/analytics/logs/dag_id=vectornode_anomaly_etl/run_id=manual_009/task_id=load_raw/attempt=1.log 2>&1'
stdin2, stdout2, stderr2 = ssh.exec_command(cmd2)
print('\nTail:')
print(stdout2.read().decode(errors='replace').strip()[:500])

ssh.close()
