import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

cmd = (
    '. /opt/analytics/venv/bin/activate && AIRFLOW_HOME=/opt/analytics '
    'airflow tasks states-for-dag-run analytics_pipeline test_manual 2>&1'
)
stdin, stdout, stderr = ssh.exec_command(cmd)
print(stdout.read().decode(errors='replace').strip())

# Also check scheduler logs
cmd2 = 'journalctl -u airflow-scheduler --no-pager -n 15 --output=short-precise 2>&1'
stdin2, stdout2, stderr2 = ssh.exec_command(cmd2)
print('\nScheduler logs:')
print(stdout2.read().decode(errors='replace').strip()[:1000])

ssh.close()
