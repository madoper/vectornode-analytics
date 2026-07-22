import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

cmds = [
    'systemctl is-enabled airflow-webserver airflow-scheduler',
    'dbt --version 2>/dev/null || echo "dbt not found"',
    '. /opt/analytics/venv/bin/activate && dbt --version 2>&1',
]

for cmd in cmds:
    print(f'=== {cmd} ===')
    stdin, stdout, stderr = ssh.exec_command(cmd)
    print(stdout.read().decode(errors='replace').strip())

ssh.close()
