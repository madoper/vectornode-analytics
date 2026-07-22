import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

# Find error location
cmd = "grep -n 'Error\\|error\\|Traceback\\|Undefined\\|Cannot\\|failed\\|syntax' /opt/analytics/logs/dag_id=vectornode_anomaly_etl/run_id=manual_008/task_id=load_raw/attempt=1.log | head -10"
stdin, stdout, stderr = ssh.exec_command(cmd)
print(stdout.read().decode(errors='replace').strip())

# Read around the error
cmd2 = "grep -n 'COPY\\|CREATE\\|DROP\\|cur.execute\\|copy_from' /opt/analytics/logs/dag_id=vectornode_anomaly_etl/run_id=manual_008/task_id=load_raw/attempt=1.log"
stdin2, stdout2, stderr2 = ssh.exec_command(cmd2)
print('\nSQL operations:')
print(stdout2.read().decode(errors='replace').strip())

ssh.close()
