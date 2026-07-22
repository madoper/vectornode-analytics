import paramiko, time, json
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', port=22, username='root', password='8884&JKL%f75', timeout=15)

# 1. Deploy DAG to server
sftp = ssh.open_sftp()
sftp.put(r'D:\project\FRS_TEST\airflow\dags\anomaly_etl.py', '/opt/analytics/dags/anomaly_etl.py')
sftp.close()
print('1. DAG deployed')

# 2. Restart Airflow
_, so, _ = ssh.exec_command('systemctl restart airflow-webserver airflow-scheduler 2>&1')
print('2. Airflow restarted')
time.sleep(10)

# 3. Trigger DAG
_, so2, _ = ssh.exec_command(
    '. /opt/analytics/venv/bin/activate && AIRFLOW_HOME=/opt/analytics '
    'airflow dags trigger -r fix_v2_001 vectornode_anomaly_etl 2>&1'
)
print('3. DAG triggered:', so2.read().decode(errors='replace')[:200])
print('   Waiting 90s for completion...')
time.sleep(90)

# 4. Check results
queries = [
    "SELECT COUNT(*) FROM analytics.company",
    "SELECT COUNT(*) FROM analytics.company_year",
    "SELECT COUNT(DISTINCT company_id || '-' || year) FROM analytics.v_company_dashboard",
    "SELECT COUNT(*) FROM analytics.anomaly",
    "SELECT criticality, COUNT(*) FROM analytics.anomaly GROUP BY criticality ORDER BY criticality",
    "SELECT interpretation, COUNT(*) FROM analytics.anomaly GROUP BY interpretation",
    "SELECT hypothesis_code, COUNT(*) FROM analytics.anomaly GROUP BY hypothesis_code ORDER BY hypothesis_code",
]
for q in queries:
    _, o, _ = ssh.exec_command(
        'docker exec podft-postgres psql -U podft -d analytics -c "' + q + '"'
    )
    print(f'  {o.read().decode(errors="replace").strip()}')

# 5. Check by C0412 specific (P1 fix)
_, o3, _ = ssh.exec_command(
    'docker exec podft-postgres psql -U podft -d analytics -t -A -c '
    '"SELECT cy.company_id, cy.year, a.hypothesis_code FROM analytics.company_year cy '
    'LEFT JOIN analytics.anomaly a ON a.company_id = cy.company_id AND a.year = cy.year '
    'WHERE cy.company_id = \'C0412\' AND cy.year = 2023 ORDER BY a.hypothesis_code"'
)
print(f'\nP1 check (C0412 2023 anomalies):')
for line in o3.read().decode(errors='replace').split('\n'):
    if line.strip():
        print(f'  {line}')

# 6. Sync Superset dataset
_, auth, _ = ssh.exec_command(
    'curl -s -X POST http://127.0.0.1:8088/api/v1/security/login '
    '-H "Content-Type: application/json" '
    '-d \'{"username":"admin","password":"admin","provider":"db"}\''
)
token = json.loads(auth.read().decode(errors='replace'))["access_token"]
_, so4, _ = ssh.exec_command(
    'curl -s -X PUT "http://127.0.0.1:8088/api/v1/dataset/3/refresh" '
    '-H "Content-Type: application/json" '
    '-H "Authorization: Bearer ' + token + '" -d \'{"datasource_type": "table"}\''
)
print(f'\nSuperset sync: {so4.read().decode(errors="replace").strip()}')

ssh.close()
