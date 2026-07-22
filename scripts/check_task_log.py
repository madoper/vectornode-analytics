import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

# Check task log for the failed task
cmd = (
    '. /opt/analytics/venv/bin/activate && AIRFLOW_HOME=/opt/analytics '
    'airflow tasks log analytics_pipeline run_ml_anomaly_detection test_manual 2>&1 | tail -20'
)
stdin, stdout, stderr = ssh.exec_command(cmd)
print(stdout.read().decode(errors='replace').strip()[:1000])

ssh.close()
