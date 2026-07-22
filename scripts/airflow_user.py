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
    'cd /opt/analytics\n\n'
    'airflow db check 2>&1\n'
    'echo "---\n"\n'
    'airflow users list 2>&1\n'
    'echo "---\n"\n'
    'airflow users create '
    '--username admin --firstname Admin --lastname User '
    '--role Admin --email admin@vectornode.ru --password admin123 2>&1\n'
)

stdin, stdout, stderr = ssh.exec_command(script)
import sys
for line in iter(stdout.readline, ''):
    print(line, end='')
    sys.stdout.flush()
print('Exit:', stdout.channel.recv_exit_status())
ssh.close()
