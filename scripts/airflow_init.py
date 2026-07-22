import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

script = (
    'export AIRFLOW_HOME=/opt/analytics\n'
    'export PATH=/opt/analytics/venv/bin:$PATH\n'
    'export AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=postgresql+psycopg2://airflow_user:airflow_pass@localhost:5432/airflow_db\n'
    'export AIRFLOW__CORE__EXECUTOR=SequentialExecutor\n'
    'export AIRFLOW__CORE__LOAD_EXAMPLES=False\n'
    'export AIRFLOW__CORE__DAGS_FOLDER=/opt/analytics/dags\n'
    'export AIRFLOW__WEBSERVER__WEB_SERVER_PORT=8080\n'
    'export AIRFLOW__WEBSERVER__EXPOSE_CONFIG=True\n'
    'export AIRFLOW__SCHEDULER__DAG_DIR_LIST_INTERVAL=30\n'
    'cd /opt/analytics\n'
    'rm -f airflow.cfg airflow.db\n'
    'airflow db migrate 2>&1\n'
    'echo "DB_INIT_DONE=$?"\n'
)

print('Running script on server...')
stdin, stdout, stderr = ssh.exec_command(script)
import sys
for line in iter(stdout.readline, ''):
    print(line, end='')
    sys.stdout.flush()
exit_code = stdout.channel.recv_exit_status()
print('Exit:', exit_code)

if exit_code == 0:
    stdin2, stdout2, stderr2 = ssh.exec_command(
        'export AIRFLOW_HOME=/opt/analytics && '
        'export PATH=/opt/analytics/venv/bin:$PATH && '
        'airflow users create '
        '--username admin --firstname Admin --lastname User '
        '--role Admin --email admin@vectornode.ru --password admin123 2>&1'
    )
    for line in iter(stdout2.readline, ''):
        print(line, end='')
        sys.stdout.flush()
    print('User create exit:', stdout2.channel.recv_exit_status())

# Check config was written
stdin3, stdout3, stderr3 = ssh.exec_command(
    'export AIRFLOW_HOME=/opt/analytics && '
    'cat /opt/analytics/airflow.cfg | head -5'
)
print('\nairflow.cfg:')
print(stdout3.read().decode().strip())

ssh.close()
