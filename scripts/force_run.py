import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

# Check if DAG is paused
stdin, stdout, stderr = ssh.exec_command('. /opt/analytics/venv/bin/activate && AIRFLOW_HOME=/opt/analytics airflow dags details vectornode_anomaly_etl 2>&1 | grep -i "is_paused"')
print('Paused:', stdout.read().decode(errors='replace').strip())

# Unpause
stdin2, stdout2, stderr2 = ssh.exec_command('. /opt/analytics/venv/bin/activate && AIRFLOW_HOME=/opt/analytics airflow dags unpause vectornode_anomaly_etl 2>&1')
print('Unpause:', stdout2.read().decode(errors='replace').strip()[:200])

# Restart scheduler
ssh.exec_command('systemctl restart airflow-scheduler 2>&1')
import time
time.sleep(5)

# Trigger new run
stdin3, stdout3, stderr3 = ssh.exec_command('. /opt/analytics/venv/bin/activate && AIRFLOW_HOME=/opt/analytics airflow dags trigger -r manual_005 vectornode_anomaly_etl 2>&1')
print('Trigger:', stdout3.read().decode(errors='replace').strip()[:200])

ssh.close()
