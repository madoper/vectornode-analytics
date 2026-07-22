import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

commands = [
    'ls -la /opt/analytics/venv/bin/airflow 2>/dev/null || echo "airflow not in venv/bin"',
    'source /opt/analytics/venv/bin/activate && which airflow 2>/dev/null || echo "airflow not in PATH after source"',
    '. /opt/analytics/venv/bin/activate && python -c "import airflow; print(airflow.__version__)" 2>/dev/null || echo "not importable"',
    '. /opt/analytics/venv/bin/activate && pip list 2>/dev/null | grep -i airflow',
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
