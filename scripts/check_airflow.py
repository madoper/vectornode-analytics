import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=10)

cmds = [
    'systemctl is-active airflow-webserver airflow-scheduler',
    '. /opt/analytics/venv/bin/activate && AIRFLOW_HOME=/opt/analytics airflow users list 2>&1',
]

for cmd in cmds:
    stdin, stdout, stderr = ssh.exec_command(cmd)
    print(stdout.read().decode(errors='replace').strip()[:500])

ssh.close()
