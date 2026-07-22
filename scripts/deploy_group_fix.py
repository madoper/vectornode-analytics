import paramiko, time, json, urllib.parse
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', port=22, username='root', password='8884&JKL%f75', timeout=15)

sftp = ssh.open_sftp()
sftp.put(r'D:\project\FRS_TEST\airflow\dags\anomaly_etl.py', '/opt/analytics/dags/anomaly_etl.py')
sftp.close()
print('1. DAG deployed')

_, so, _ = ssh.exec_command('systemctl restart airflow-webserver airflow-scheduler 2>&1')
print('2. Airflow restarted')
time.sleep(10)

_, so2, _ = ssh.exec_command(
    '. /opt/analytics/venv/bin/activate && AIRFLOW_HOME=/opt/analytics '
    'airflow dags trigger -r fix_group_signal vectornode_anomaly_etl 2>&1'
)
print('3. DAG triggered')
print('   Waiting 120s...')
time.sleep(120)

# Check rpt_group_signal results
queries = [
    "SELECT COUNT(1) FROM reporting.rpt_group_signal",
    "SELECT interpretation_final, COUNT(1) FROM reporting.rpt_group_signal GROUP BY interpretation_final",
    "SELECT criticality_final, COUNT(1) FROM reporting.rpt_group_signal GROUP BY criticality_final",
]
for q in queries:
    _, o, _ = ssh.exec_command(f'docker exec podft-postgres psql -U podft -d analytics -c "{q}"')
    print(o.read().decode(errors='replace').strip())
    print('---')

# Check specific groups
_, o3, _ = ssh.exec_command(
    "docker exec podft-postgres psql -U podft -d analytics -c "
    "\"SELECT group_key, companies_count, risk_companies_count, anomaly_count, max_criticality_score, interpretation_final, criticality_final "
    "FROM reporting.rpt_group_signal WHERE max_criticality_score >= 4 ORDER BY max_criticality_score DESC LIMIT 8\""
)
print('High-score groups:')
print(o3.read().decode(errors='replace'))

# Sync Superset dataset
_, auth, _ = ssh.exec_command(
    'curl -s -X POST http://127.0.0.1:8088/api/v1/security/login '
    '-H "Content-Type: application/json" '
    '-d \'{"username":"admin","password":"admin","provider":"db"}\''
)
token = json.loads(auth.read().decode(errors='replace'))["access_token"]

_, ref, _ = ssh.exec_command(
    'curl -s -X PUT "http://127.0.0.1:8088/api/v1/dataset/7/refresh" '
    '-H "Content-Type: application/json" '
    '-H "Authorization: Bearer ' + token + '" '
    '-d \'{"datasource_type": "table"}\''
)
print(f'Superset sync: {ref.read().decode(errors="replace").strip()}')

ssh.close()
