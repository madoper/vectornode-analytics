import paramiko, json
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', port=22, username='root', password='8884&JKL%f75', timeout=10)

_, auth, _ = ssh.exec_command(
    'curl -s -X POST http://127.0.0.1:8088/api/v1/security/login '
    '-H "Content-Type: application/json" '
    '-d \'{"username":"admin","password":"admin","provider":"db"}\''
)
token = json.loads(auth.read().decode(errors='replace'))["access_token"]

# List existing datasets
_, ds_resp, _ = ssh.exec_command(
    'curl -s http://127.0.0.1:8088/api/v1/dataset/ -H "Authorization: Bearer ' + token + '"'
)
datasets = {d['table_name']: d['id'] for d in json.loads(ds_resp.read().decode(errors='replace')).get('result', [])}
print('Existing datasets:', {k: v for k, v in datasets.items() if k.startswith('rpt_')})

# Register new datasets
for tbl, tbl_name in [
    ("rpt_anomaly", "Аномалии (детали)"),
    ("rpt_company_hypothesis_flags", "Флаги гипотез H1-H6"),
    ("rpt_company_year", "Витрина компаний"),
    ("rpt_group_signal", "Групповые сигналы"),
    ("rpt_hypothesis_summary", "Сводка гипотез"),
]:
    if tbl in datasets:
        # Refresh existing
        _, ref, _ = ssh.exec_command(
            'curl -s -X PUT "http://127.0.0.1:8088/api/v1/dataset/' + str(datasets[tbl]) + '/refresh" '
            '-H "Content-Type: application/json" '
            '-H "Authorization: Bearer ' + token + '" '
            '-d \'{"datasource_type": "table"}\''
        )
        print(f'  Refreshed: {tbl_name} (id={datasets[tbl]})')
    else:
        # Create new
        _, reg, _ = ssh.exec_command(
            'curl -s -X POST "http://127.0.0.1:8088/api/v1/dataset/" '
            '-H "Content-Type: application/json" '
            '-H "Authorization: Bearer ' + token + '" '
            '-d \'{"database":1,"schema":"reporting","table_name":"' + tbl + '"}\''
        )
        result = json.loads(reg.read().decode(errors='replace'))
        rid = result.get('id')
        if rid:
            # Refresh columns
            _, ref2, _ = ssh.exec_command(
                'curl -s -X PUT "http://127.0.0.1:8088/api/v1/dataset/' + str(rid) + '/refresh" '
                '-H "Content-Type: application/json" '
                '-H "Authorization: Bearer ' + token + '" '
                '-d \'{"datasource_type": "table"}\''
            )
            print(f'  Created: {tbl_name} (id={rid})')
        else:
            print(f'  Failed: {tbl_name} - {json.dumps(result)}')

# Set superset config for FEATURE_FLAGS to enable native filters
_, cf, _ = ssh.exec_command(
    'curl -s -X PUT "http://127.0.0.1:8088/api/v1/dataset/_info" '
    '-H "Content-Type: application/json" '
    '-H "Authorization: Bearer ' + token + '"'
)

print('\nDone!')
print('Reporting tables:')
for tbl in ['rpt_anomaly', 'rpt_company_hypothesis_flags', 'rpt_company_year', 'rpt_group_signal', 'rpt_hypothesis_summary']:
    _, cnt, _ = ssh.exec_command(
        'docker exec podft-postgres psql -U podft -d analytics -t -A -c '
        '\"SELECT COUNT(1) FROM reporting.' + tbl + '\"'
    )
    print(f'  {tbl}: {cnt.read().decode(errors="replace").strip()} rows')

ssh.close()
