import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)
sftp = ssh.open_sftp()
sftp.put(r'D:\project\FRS_TEST\scripts\ml_anomaly_detection.py', '/opt/analytics/scripts/ml_anomaly_detection.py')
sftp.close()
print('Uploaded')

stdin, stdout, stderr = ssh.exec_command(
    'cd /opt/analytics && . venv/bin/activate && python scripts/ml_anomaly_detection.py 2>&1'
)
print(stdout.read().decode(errors='replace'))
ssh.close()
