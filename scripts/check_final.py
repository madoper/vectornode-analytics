import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

cmd = (
    '. /opt/analytics/venv/bin/activate && AIRFLOW_HOME=/opt/analytics '
    'airflow tasks states-for-dag-run analytics_pipeline test_manual2 2>&1 | grep -v graphviz'
)
stdin, stdout, stderr = ssh.exec_command(cmd)
print(stdout.read().decode(errors='replace').strip())

# Check the dbt log  
cmd2 = 'cat /opt/analytics/logs/dag_id=analytics_pipeline/run_id=test_manual2/task_id=run_dbt_transformations/attempt=1.log 2>&1 | grep -E "Completed|ERROR|error" | head -3'
stdin2, stdout2, stderr2 = ssh.exec_command(cmd2)
print('dbt log:', stdout2.read().decode(errors='replace').strip()[:500])

ssh.close()
