import paramiko, time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

time.sleep(20)

cmd = (
    '. /opt/analytics/venv/bin/activate && AIRFLOW_HOME=/opt/analytics '
    'airflow tasks states-for-dag-run analytics_pipeline test_manual2 2>&1 | grep -v graphviz'
)
stdin, stdout, stderr = ssh.exec_command(cmd)
print(stdout.read().decode(errors='replace').strip()[:500])

# Run states for dbt task
time.sleep(5)
cmd2 = (
    '. /opt/analytics/venv/bin/activate && AIRFLOW_HOME=/opt/analytics '
    'airflow tasks states-for-dag-run analytics_pipeline test_manual2 2>&1 | grep -v graphviz'
)
stdin2, stdout2, stderr2 = ssh.exec_command(cmd2)
print('Final states:')
print(stdout2.read().decode(errors='replace').strip()[:500])

ssh.close()
