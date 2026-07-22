import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

cmds = [
    '. /opt/analytics/venv/bin/activate && AIRFLOW_HOME=/opt/analytics airflow dags list-runs -d vectornode_anomaly_etl 2>&1',
    'systemctl is-active airflow-scheduler',
]

for cmd in cmds:
    stdin, stdout, stderr = ssh.exec_command(cmd)
    print(f'> {cmd[:60]}')
    print(stdout.read().decode(errors='replace').strip()[:500])

ssh.close()
