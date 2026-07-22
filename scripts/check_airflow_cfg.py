import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

# Read current airflow.cfg
stdin, stdout, stderr = ssh.exec_command('grep -n "sql_alchemy_conn\|executor\|load_examples\|dags_folder" /opt/analytics/airflow.cfg')
print('Current config:')
print(stdout.read().decode(errors='replace').strip())

# Check if env vars override works
stdin2, stdout2, stderr2 = ssh.exec_command(
    '. /opt/analytics/venv/bin/activate && AIRFLOW_HOME=/opt/analytics '
    'AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=postgresql+psycopg2://airflow_user:airflow_pass@localhost:5432/airflow_db '
    'airflow dags list 2>&1 | head -10'
)
print('DAG list with env override:')
print(stdout2.read().decode(errors='replace').strip()[:500])

ssh.close()
