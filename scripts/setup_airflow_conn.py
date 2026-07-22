import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=30)

cmds = [
    'export AIRFLOW_HOME=/opt/analytics && export PATH=/opt/analytics/venv/bin:$PATH && airflow connections delete analytics_db 2>/dev/null; airflow connections add analytics_db --conn-type postgres --conn-host localhost --conn-port 5432 --conn-login dbt_user --conn-password dbt_pass --conn-schema analytics',
    'export AIRFLOW_HOME=/opt/analytics && export PATH=/opt/analytics/venv/bin:$PATH && airflow variables set z_critical 3.0 && airflow variables set z_high 2.0 && airflow variables set payout_critical 1.5',
    'export AIRFLOW_HOME=/opt/analytics && export PATH=/opt/analytics/venv/bin:$PATH && airflow variables set payout_high 1.0 && airflow variables set rev_growth_high 0.30 && airflow variables set emp_growth_high -0.10',
    'export AIRFLOW_HOME=/opt/analytics && export PATH=/opt/analytics/venv/bin:$PATH && airflow variables set fin_pressure_critical 2.0 && airflow variables set fin_pressure_high 1.2 && airflow variables set multi_flags_critical 3',
]

for cmd in cmds:
    stdin, stdout, stderr = ssh.exec_command(cmd)
    out = stdout.read().decode(errors='replace').strip()
    if out:
        print(out[:200])

ssh.close()
print('Done')
