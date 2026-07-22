import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

cmds = [
    'echo "=== SERVICES ==="',
    'systemctl show -p ActiveState airflow-webserver airflow-scheduler',
    'echo "=== AIRFLOW DAG LIST ==="',
    '. /opt/analytics/venv/bin/activate && AIRFLOW_HOME=/opt/analytics airflow dags list 2>&1',
    'echo "=== AIRFLOW CONNECTION CHECK ==="',
    '. /opt/analytics/venv/bin/activate && AIRFLOW_HOME=/opt/analytics airflow db check 2>&1',
    'echo "=== ANALYTICS DB DATA ==="',
    'docker exec podft-postgres psql -U dbt_user -d analytics -c "SELECT * FROM public_marts.company_risk_summary ORDER BY anomaly_pct DESC"',
    'echo "=== DBT TEST ==="',
    'cd /opt/analytics/analytics_dbt && . /opt/analytics/venv/bin/activate && dbt test --profiles-dir . --project-dir . 2>&1 || true',
]

for cmd in cmds:
    print(f'> {cmd[:70]}')
    stdin, stdout, stderr = ssh.exec_command(cmd)
    print(stdout.read().decode(errors='replace').strip()[:2000])

ssh.close()
