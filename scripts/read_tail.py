import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

stdin, stdout, stderr = ssh.exec_command('wc -l /opt/analytics/logs/dag_id=vectornode_anomaly_etl/run_id=manual_007/task_id=load_raw/attempt=1.log')
total = int(stdout.read().decode().strip().split()[0])
print(f'Total lines: {total}')

stdin2, stdout2, stderr2 = ssh.exec_command(f'tail -{min(30, total)} /opt/analytics/logs/dag_id=vectornode_anomaly_etl/run_id=manual_007/task_id=load_raw/attempt=1.log 2>&1')
print(stdout2.read().decode(errors='replace').strip())

ssh.close()
