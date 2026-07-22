import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

cmd = 'cat /opt/analytics/logs/dag_id=vectornode_anomaly_etl/run_id=manual_003/task_id=load_raw/attempt=1.log 2>&1 | tail -15'
stdin, stdout, stderr = ssh.exec_command(cmd)
print(stdout.read().decode(errors='replace').strip())

ssh.close()
