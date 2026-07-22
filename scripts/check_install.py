import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

commands = [
    'ls -la /opt/analytics/',
    'cat /opt/analytics/install_airflow.sh',
    'ls -la /opt/analytics/airflow_env/bin/airflow 2>/dev/null || echo "airflow not found in env"',
    'which airflow 2>/dev/null || /opt/analytics/airflow_env/bin/python -c "import airflow; print(airflow.__version__)" 2>/dev/null || echo "airflow not importable"',
    'ls -d /opt/analytics/airflow_env/*python*/site-packages/airflow 2>/dev/null || echo "no airflow site-packages"',
]

for cmd in commands:
    print('$ ' + cmd)
    stdin, stdout, stderr = ssh.exec_command(cmd)
    out = stdout.read().decode().strip()
    err = stderr.read().decode().strip()
    if out:
        print(out)
    if err:
        print('STDERR:', err)
    print()

ssh.close()
