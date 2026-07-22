import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

# Read airflow.cfg
stdin, stdout, stderr = ssh.exec_command('cat /opt/analytics/airflow.cfg')
cfg_data = stdout.read().decode(errors='replace')

# Replace key values
cfg_data = cfg_data.replace('sql_alchemy_conn = sqlite:////opt/analytics/airflow.db',
                             'sql_alchemy_conn = postgresql+psycopg2://airflow_user:airflow_pass@localhost:5432/airflow_db')
cfg_data = cfg_data.replace('load_examples = True',
                             'load_examples = False')

# Write back
sftp = ssh.open_sftp()
with sftp.open('/opt/analytics/airflow.cfg', 'w') as f:
    f.write(cfg_data.encode())
sftp.close()
print('airflow.cfg updated')

# Verify
stdin2, stdout2, stderr2 = ssh.exec_command('grep -n "sql_alchemy_conn\|load_examples" /opt/analytics/airflow.cfg | head -5')
print(stdout2.read().decode(errors='replace').strip())

# Restart services to pick up new config
stdin3, stdout3, stderr3 = ssh.exec_command('systemctl restart airflow-webserver airflow-scheduler && sleep 3 && systemctl show -p ActiveState airflow-webserver airflow-scheduler')
print(stdout3.read().decode(errors='replace').strip())

# Test DAG list now
stdin4, stdout4, stderr4 = ssh.exec_command(
    '. /opt/analytics/venv/bin/activate && AIRFLOW_HOME=/opt/analytics airflow dags list 2>&1 | grep -v graphviz'
)
print('DAGs:', stdout4.read().decode(errors='replace').strip())

ssh.close()
