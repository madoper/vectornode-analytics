import paramiko, time, json, urllib.parse
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', port=22, username='root', password='8884&JKL%f75', timeout=15)

# Deploy DAG
sftp = ssh.open_sftp()
sftp.put(r'D:\project\FRS_TEST\airflow\dags\anomaly_etl.py', '/opt/analytics/dags/anomaly_etl.py')
sftp.close()
print('1. DAG deployed')

# Restart Airflow
_, so, _ = ssh.exec_command('systemctl restart airflow-webserver airflow-scheduler 2>&1')
print('2. Airflow restarted')
time.sleep(10)

# Trigger DAG
_, so2, _ = ssh.exec_command(
    '. /opt/analytics/venv/bin/activate && AIRFLOW_HOME=/opt/analytics '
    'airflow dags trigger -r reporting_v1 vectornode_anomaly_etl 2>&1'
)
print('3. DAG triggered:', so2.read().decode(errors='replace')[:200])
print('   Waiting 120s...')
time.sleep(120)

# Check results
queries = [
    ("company", "SELECT COUNT(1) FROM analytics.company"),
    ("company_year", "SELECT COUNT(1) FROM analytics.company_year"),
    ("anomaly", "SELECT hypothesis_code, COUNT(1) FROM analytics.anomaly GROUP BY hypothesis_code ORDER BY hypothesis_code"),
    ("rpt_anomaly", "SELECT COUNT(1) FROM reporting.rpt_anomaly"),
    ("rpt_company_hypothesis_flags", "SELECT COUNT(1) FROM reporting.rpt_company_hypothesis_flags"),
    ("rpt_company_year", "SELECT COUNT(1) FROM reporting.rpt_company_year"),
    ("rpt_group_signal", "SELECT COUNT(1) FROM reporting.rpt_group_signal"),
    ("rpt_hypothesis_summary", "SELECT COUNT(1) FROM reporting.rpt_hypothesis_summary"),
]
for name, q in queries:
    _, o, _ = ssh.exec_command(
        'docker exec podft-postgres psql -U podft -d analytics -c "' + q + '"'
    )
    out = o.read().decode(errors='replace').strip()
    print(f'\n{name}:')
    for line in out.split('\n')[:5]:
        print(f'  {line}')

# Register Superset datasets
_, auth, _ = ssh.exec_command(
    'curl -s -X POST http://127.0.0.1:8088/api/v1/security/login '
    '-H "Content-Type: application/json" '
    '-d \'{"username":"admin","password":"admin","provider":"db"}\''
)
token = json.loads(auth.read().decode(errors='replace'))["access_token"]

# Get database ID
_, db_resp, _ = ssh.exec_command(
    'curl -s http://127.0.0.1:8088/api/v1/database/ -H "Authorization: Bearer ' + token + '"'
)
dbs = json.loads(db_resp.read().decode(errors='replace'))
db_id = None
for d in dbs.get('result', []):
    if 'analytics' in str(d.get('database_name', '')).lower() or 'dbt' in str(d.get('database_name', '')).lower():
        db_id = d['id']
        print(f'\nDatabase: {d["database_name"]} (id={db_id})')
        break

if not db_id:
    db_id = 1

# Register datasets
for tbl, tbl_name, sch in [
    ("rpt_anomaly", "reporting", "Детальные аномалии"),
    ("rpt_company_hypothesis_flags", "reporting", "Флаги гипотез"),
    ("rpt_company_year", "reporting", "Витрина компаний"),
    ("rpt_group_signal", "reporting", "Групповые сигналы"),
    ("rpt_hypothesis_summary", "reporting", "Сводка гипотез"),
]:
    # Check if exists
    _, check, _ = ssh.exec_command(
        'docker exec podft-postgres psql -U podft -d superset -t -A -c '
        '\"SELECT id FROM tables WHERE table_name = \'' + tbl + '\' AND schema = \'' + sch + '\' AND database_id = ' + str(db_id) + '\"'
    )
    existing = check.read().decode(errors='replace').strip()
    if not existing:
        _, reg, _ = ssh.exec_command(
            'curl -s -X POST "http://127.0.0.1:8088/api/v1/dataset/" '
            '-H "Content-Type: application/json" '
            '-H "Authorization: Bearer ' + token + '" '
            '-d \'{"database":' + str(db_id) + ',"schema":"' + sch + '","table_name":"' + tbl + '"}\''
        )
        result = json.loads(reg.read().decode(errors='replace'))
        if result.get('id'):
            # Refresh columns
            _, ref, _ = ssh.exec_command(
                'curl -s -X PUT "http://127.0.0.1:8088/api/v1/dataset/' + str(result['id']) + '/refresh" '
                '-H "Content-Type: application/json" '
                '-H "Authorization: Bearer ' + token + '" '
                '-d \'{"datasource_type": "table"}\''
            )
            print(f'  Registered: {tbl_name} (id={result["id"]})')
        else:
            print(f'  Failed: {tbl_name} - {reg.read().decode(errors="replace")[:100]}')
    else:
        print(f'  Exists: {tbl_name} (id={existing})')

# Also refresh existing v_company_dashboard dataset
_, ref2, _ = ssh.exec_command(
    'curl -s -X PUT "http://127.0.0.1:8088/api/v1/dataset/3/refresh" '
    '-H "Content-Type: application/json" '
    '-H "Authorization: Bearer ' + token + '" '
    '-d \'{"datasource_type": "table"}\''
)
print(f'\nRefreshed v_company_dashboard: {ref2.read().decode(errors="replace").strip()}')

ssh.close()
