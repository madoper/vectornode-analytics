import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=10)

# Verify user
stdin, stdout, stderr = ssh.exec_command('. /opt/analytics/venv/bin/activate && AIRFLOW_HOME=/opt/analytics airflow users list 2>&1 | grep -v Warning')
print('Users:', stdout.read().decode(errors='replace').strip()[:300])

# Restart webserver
ssh.exec_command('systemctl restart airflow-webserver')
import time
time.sleep(3)
stdin2, stdout2, stderr2 = ssh.exec_command('systemctl is-active airflow-webserver')
print('Webserver:', stdout2.read().decode(errors='replace').strip())

ssh.close()
