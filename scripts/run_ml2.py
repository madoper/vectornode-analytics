import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

cmd = (
    'cd /opt/analytics && '
    '. venv/bin/activate && '
    'python scripts/ml_anomaly_detection.py 2>&1'
)

stdin, stdout, stderr = ssh.exec_command(cmd)
out = stdout.read().decode(errors='replace')
print(out)
ssh.close()
