import paramiko, time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

time.sleep(15)

cmd = (
    '. /opt/analytics/venv/bin/activate && AIRFLOW_HOME=/opt/analytics '
    'airflow tasks states-for-dag-run analytics_pipeline test_manual 2>&1 | grep -v graphviz'
)
stdin, stdout, stderr = ssh.exec_command(cmd)
print('Manual run tasks:')
print(stdout.read().decode(errors='replace').strip())

cmd2 = (
    '. /opt/analytics/venv/bin/activate && AIRFLOW_HOME=/opt/analytics '
    'airflow tasks states-for-dag-run analytics_pipeline "scheduled__2026-07-13T06:00:00+00:00" 2>&1 | grep -v graphviz'
)
stdin2, stdout2, stderr2 = ssh.exec_command(cmd2)
print('\nScheduled run tasks:')
print(stdout2.read().decode(errors='replace').strip())

ssh.close()
