import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

sftp = ssh.open_sftp()
sftp.put(r'D:\project\FRS_TEST\airflow\dags\anomaly_etl.py', '/opt/analytics/dags/anomaly_etl.py')
sftp.close()
print('DAG uploaded')

# Create Airflow connection
cmds = """
export AIRFLOW_HOME=/opt/analytics
export PATH=/opt/analytics/venv/bin:$PATH
airflow connections delete analytics_db 2>/dev/null
airflow connections add analytics_db \
  --conn-type postgres \
  --conn-host localhost \
  --conn-port 5432 \
  --conn-login dbt_user \
  --conn-password dbt_pass \
  --conn-schema analytics 2>&1
"""
stdin, stdout, stderr = ssh.exec_command(cmds)
print('Connection:', stdout.read().decode(errors='replace').strip())

# Set Variables
vars_cmd = """
export AIRFLOW_HOME=/opt/analytics
export PATH=/opt/analytics/venv/bin:$PATH
airflow variables set z_critical 3.0
airflow variables set z_high 2.0
airflow variables set payout_critical 1.5
airflow variables set payout_high 1.0
airflow variables set rev_growth_high 0.30
airflow variables set emp_growth_high -0.10
airflow variables set fin_pressure_critical 2.0
airflow variables set fin_pressure_high 1.2
airflow variables set multi_flags_critical 3
echo "Variables set"
"""
stdin2, stdout2, stderr2 = ssh.exec_command(vars_cmd)
print('Variables:', stdout2.read().decode(errors='replace').strip())

# List DAGs
dags_cmd = """
export AIRFLOW_HOME=/opt/analytics
export PATH=/opt/analytics/venv/bin:$PATH
airflow dags list 2>&1 | grep -v graphviz
"""
stdin3, stdout3, stderr3 = ssh.exec_command(dags_cmd)
print('DAGs:')
print(stdout3.read().decode(errors='replace').strip())

ssh.close()
