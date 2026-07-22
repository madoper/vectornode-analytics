import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

# Start services individually to capture errors
cmds = [
    'systemctl start airflow-webserver 2>&1; echo "WEBSERVER_EXIT=$?"',
    'systemctl start airflow-scheduler 2>&1; echo "SCHEDULER_EXIT=$?"',
    'sleep 3',
    'systemctl show -p ActiveState airflow-webserver 2>&1',
    'systemctl show -p ActiveState airflow-scheduler 2>&1',
    'journalctl -u airflow-webserver --no-pager -n 10 --output=short-precise 2>&1',
    'journalctl -u airflow-scheduler --no-pager -n 10 --output=short-precise 2>&1',
]

for cmd in cmds:
    print(f'> {cmd}')
    stdin, stdout, stderr = ssh.exec_command(cmd)
    print(stdout.read().decode(errors='replace').strip())

ssh.close()
