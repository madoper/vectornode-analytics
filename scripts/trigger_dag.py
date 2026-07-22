import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

cmds = [
    '. /opt/analytics/venv/bin/activate && AIRFLOW_HOME=/opt/analytics airflow dags unpause analytics_pipeline 2>&1',
    '. /opt/analytics/venv/bin/activate && AIRFLOW_HOME=/opt/analytics airflow dags trigger -r test_manual analytics_pipeline 2>&1',
    'sleep 5',
    '. /opt/analytics/venv/bin/activate && AIRFLOW_HOME=/opt/analytics airflow dags list-runs -d analytics_pipeline 2>&1 | head -10',
]

for cmd in cmds:
    print(f'> {cmd[:70]}')
    stdin, stdout, stderr = ssh.exec_command(cmd)
    print(stdout.read().decode(errors='replace').strip()[:500])

ssh.close()
