import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

cmd = "sed -n '14,45p' /opt/analytics/logs/dag_id=vectornode_anomaly_etl/run_id=manual_008/task_id=load_raw/attempt=1.log"
stdin, stdout, stderr = ssh.exec_command(cmd)
print(stdout.read().decode(errors='replace').strip()[:2000])

ssh.close()
