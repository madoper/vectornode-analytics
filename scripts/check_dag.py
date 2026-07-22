import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

cmd = (
    '. /opt/analytics/venv/bin/activate && '
    'AIRFLOW_HOME=/opt/analytics '
    'AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=postgresql+psycopg2://airflow_user:airflow_pass@localhost:5432/airflow_db '
    'airflow dags list 2>&1'
)

stdin, stdout, stderr = ssh.exec_command(cmd)
print(stdout.read().decode(errors='replace').strip()[:500])

# Check if DAG file can be parsed
cmd2 = (
    '. /opt/analytics/venv/bin/activate && '
    'python -c "import sys; sys.path.insert(0, \'/opt/analytics/dags\'); '
    'from analytics_dag import dag; print(f\'DAG: {dag.dag_id}\')" 2>&1'
)
stdin2, stdout2, stderr2 = ssh.exec_command(cmd2)
out2 = stdout2.read().decode(errors='replace')
print(f'DAG parse: {out2[:500]}')

ssh.close()
