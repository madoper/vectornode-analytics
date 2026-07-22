import paramiko, time, json, urllib.parse
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', port=22, username='root', password='8884&JKL%f75', timeout=15)

# Wait for Superset
time.sleep(30)

# 1. Status
_, so, _ = ssh.exec_command('docker ps --filter name=podft-superset --format "{{.Status}}"')
print('1. Status:', so.read().decode(errors='replace').strip())

# 2. Check filter column fix
_, so2, _ = ssh.exec_command(
    "docker exec podft-postgres psql -U podft -d superset -t -A -c "
    "\"SELECT json_metadata->'native_filter_configuration'->0->>'column' FROM dashboards WHERE id = 2\""
)
print('2. Filter column:', so2.read().decode(errors='replace').strip() or 'NULL')

# 3. Check middleware errors
_, so3, _ = ssh.exec_command('docker logs podft-superset --since 1m 2>&1 | grep -iE "syntax|traceback|error.*init|QC_LOAD|FILTER_" | tail -5')
print('3. Errors:', so3.read().decode(errors='replace').strip() or 'NONE')

# 4. Login
_, auth, _ = ssh.exec_command(
    'curl -s -X POST http://127.0.0.1:8088/api/v1/security/login -H "Content-Type: application/json" -d \'{"username":"admin","password":"admin","provider":"db"}\''
)
resp = auth.read().decode(errors='replace')
token = json.loads(resp)["access_token"] if resp.startswith('{') else None
if not token:
    time.sleep(10)
    _, auth2, _ = ssh.exec_command(
        'curl -s -X POST http://127.0.0.1:8088/api/v1/security/login -H "Content-Type: application/json" -d \'{"username":"admin","password":"admin","provider":"db"}\''
    )
    token = json.loads(auth2.read().decode())["access_token"]
print('4. Login OK')

# 5. Test chart POST without filter (no dashboard_id) → should 302 to GET
fd = urllib.parse.quote('{"slice_id":1}')
_, co, _ = ssh.exec_command(
    'curl -s -o /dev/null -w "%{http_code}" -X POST "http://127.0.0.1:8088/api/v1/chart/data?form_data=' + fd + '" '
    '-H "Content-Type: application/json" -H "Authorization: Bearer ' + token + '"'
)
code = co.read().decode(errors='replace').strip()
print(f'5. Chart POST (no dash): HTTP {code} (expect 302)')

# 6. Test chart POST with dashboard_id + filter referrer
fd2 = urllib.parse.quote('{"slice_id":1}')
_, co2, _ = ssh.exec_command(
    'curl -s -w "\nHTTP_%{http_code}" -X POST "http://127.0.0.1:8088/api/v1/chart/data?form_data=' + fd2 + '&dashboard_id=2" '
    '-H "Content-Type: application/json" '
    '-H "Authorization: Bearer ' + token + '" '
    '-H "Referer: https://bi.vectornode.ru/superset/dashboard/vectornode-anomalies/?native_filters_key=on3j7Uo8xSs"'
)
out6 = co2.read().decode(errors='replace')
if 'HTTP_200' in out6:
    if 'year = 2024' in out6 or 'year IN' in out6:
        print('6. Chart POST (filter): FILTER APPLIED!')
    elif '"query"' in out6:
        idx = out6.index('"query"')
        query = out6[idx:idx+250]
        print(f'6. Chart POST (filter): 200 (no active filter) - {query[:120]}')
    else:
        print(f'6. Chart POST (filter): 200 OK')
else:
    print(f'6. Chart POST (filter): {out6[:200]}')

# 7. Test native filter POST
_, co3, _ = ssh.exec_command(
    'curl -s -o /dev/null -w "%{http_code}" -X POST http://127.0.0.1:8088/api/v1/chart/data '
    '-H "Content-Type: application/json" '
    '-H "Authorization: Bearer ' + token + '" '
    '-d \'{"datasource":{"id":3,"type":"table"},"queries":[{"columns":["year"],"row_limit":5}]}\''
)
print(f'7. Native filter: HTTP {co3.read().decode(errors="replace").strip()} (expect 200)')

ssh.close()
