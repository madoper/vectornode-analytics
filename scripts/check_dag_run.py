import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

# Wait for execution and check status
cmd = (
    '. /opt/analytics/venv/bin/activate && AIRFLOW_HOME=/opt/analytics '
    'airflow dags list-runs -d analytics_pipeline 2>&1 | grep -v "graphviz\|Warning\|INFO\|Loaded"'
)
import time
time.sleep(5)

stdin, stdout, stderr = ssh.exec_command(cmd)
print(stdout.read().decode(errors='replace').strip())

# Check task instances
cmd2 = (
    '. /opt/analytics/venv/bin/activate && AIRFLOW_HOME=/opt/analytics '
    'airflow tasks list analytics_pipeline 2>&1 | grep -v graphviz'
)
stdin2, stdout2, stderr2 = ssh.exec_command(cmd2)
print(f'Tasks: {stdout2.read().decode(errors="replace").strip()}')

ssh.close()
