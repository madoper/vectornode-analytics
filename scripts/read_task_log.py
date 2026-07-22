import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

cmd = 'wc -l /opt/analytics/logs/dag_id=analytics_pipeline/run_id=test_manual/task_id=run_ml_anomaly_detection/attempt=1.log 2>&1'
stdin, stdout, stderr = ssh.exec_command(cmd)
print('Log size:', stdout.read().decode(errors='replace').strip())

cmd2 = 'cat /opt/analytics/logs/dag_id=analytics_pipeline/run_id=test_manual/task_id=run_ml_anomaly_detection/attempt=1.log 2>&1'
stdin2, stdout2, stderr2 = ssh.exec_command(cmd2)
print(stdout2.read().decode(errors='replace').strip())

ssh.close()
