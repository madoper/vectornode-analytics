import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

cmd = (
    'cd /opt/analytics/analytics_dbt && '
    '. /opt/analytics/venv/bin/activate && '
    'dbt run --profiles-dir . --project-dir . 2>&1'
)

stdin, stdout, stderr = ssh.exec_command(cmd)
print(stdout.read().decode(errors='replace'))
ssh.close()
