import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

# Check DAGs
cmd = '. /opt/analytics/venv/bin/activate && AIRFLOW_HOME=/opt/analytics airflow dags list 2>&1'
stdin, stdout, stderr = ssh.exec_command(cmd)
print('DAGs:')
print(stdout.read().decode(errors='replace').strip()[:500])

# Check connections
cmd2 = '. /opt/analytics/venv/bin/activate && AIRFLOW_HOME=/opt/analytics airflow connections list 2>&1'
stdin2, stdout2, stderr2 = ssh.exec_command(cmd2)
print('\nConnections:')
print(stdout2.read().decode(errors='replace').strip()[:500])

# Check variables
cmd3 = '. /opt/analytics/venv/bin/activate && AIRFLOW_HOME=/opt/analytics airflow variables list 2>&1'
stdin3, stdout3, stderr3 = ssh.exec_command(cmd3)
print('\nVariables:')
print(stdout3.read().decode(errors='replace').strip()[:500])

ssh.close()
