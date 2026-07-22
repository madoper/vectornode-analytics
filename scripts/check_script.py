import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

cmd = 'grep "to_sql" /opt/analytics/scripts/ml_anomaly_detection.py'
stdin, stdout, stderr = ssh.exec_command(cmd)
print(stdout.read().decode(errors='replace'))
ssh.close()
