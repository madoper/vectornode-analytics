import paramiko, time, json, urllib.parse
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', port=22, username='root', password='8884&JKL%f75', timeout=15)

V = '/var/lib/docker/volumes/podft_superset_data/_data'

# Deploy config
sftp = ssh.open_sftp()
sftp.put(r'D:\project\FRS_TEST\scripts\superset_config_clean.py', '/opt/podft/infra/superset-init/superset_config.py')
sftp.put(r'D:\project\FRS_TEST\scripts\superset_config_clean.py', f'{V}/superset_config.py')
sftp.close()
print('Config deployed')

# Clean pycache
ssh.exec_command(f'find {V} -name "*.pyc" -delete 2>/dev/null; find {V} -name "__pycache__" -exec rm -rf {{}} + 2>/dev/null')

# Restart
_, so, _ = ssh.exec_command('docker restart podft-superset')
print('Restarting...')
time.sleep(40)

# Check status
_, so2, _ = ssh.exec_command('docker ps --filter name=podft-superset --format "{{.Status}}"')
print('Status:', so2.read().decode(errors='replace').strip())

# Check for SyntaxError
_, so3, _ = ssh.exec_command('docker logs podft-superset --since 30s 2>&1 | grep -iE "syntax|traceback|FormData|middleware" | tail -5')
print('Logs:', so3.read().decode(errors='replace').strip()[:300] or 'CLEAN')

# Login
time.sleep(10)
_, auth, _ = ssh.exec_command(
    'curl -s -X POST http://127.0.0.1:8088/api/v1/security/login -H "Content-Type: application/json" -d \'{"username":"admin","password":"admin","provider":"db"}\''
)
resp = auth.read().decode(errors='replace')
token = json.loads(resp)["access_token"] if resp.startswith('{') else None
if not token:
    time.sleep(15)
    _, auth2, _ = ssh.exec_command(
        'curl -s -X POST http://127.0.0.1:8088/api/v1/security/login -H "Content-Type: application/json" -d \'{"username":"admin","password":"admin","provider":"db"}\''
    )
    token = json.loads(auth2.read().decode())["access_token"]
print('Login OK')

# TEST 1: Chart POST with slice_id + dashboard_id + native_filters_key in Referer (simulating filter)
fd = urllib.parse.quote('{"slice_id":4}')
_, co, _ = ssh.exec_command(
    'curl -s -w "\nHTTP_%{http_code}" -X POST "http://127.0.0.1:8088/api/v1/chart/data?form_data=' + fd + '&dashboard_id=2" '
    '-H "Content-Type: application/json" '
    '-H "Authorization: Bearer ' + token + '" '
    '-H "Referer: https://bi.vectornode.ru/superset/dashboard/vectornode-anomalies/?native_filters_key=on3j7Uo8xSs"'
)
out = co.read().decode(errors='replace')
print('\nTEST 1 - Chart POST with filter (slice_id=4, year filter):')
if 'year = 2024' in out:
    print('   FILTER APPLIED! year=2024 in query')
    idx = out.index('"query"')
    print('   ' + out[idx:idx+300])
elif 'HTTP_200' in out:
    print('   200 but no filter - checking query...')
    if '"query"' in out:
        idx = out.index('"query"')
        print('   ' + out[idx:idx+200])
else:
    print('   ', out[:400])

# TEST 2: Chart POST without filter (no native_filters_key in Referer)
_, co2, _ = ssh.exec_command(
    'curl -s -w "\nHTTP_%{http_code}" -X POST "http://127.0.0.1:8088/api/v1/chart/data?form_data=' + fd + '&dashboard_id=2" '
    '-H "Content-Type: application/json" '
    '-H "Authorization: Bearer ' + token + '"'
)
out2 = co2.read().decode(errors='replace')
print('\nTEST 2 - Chart POST without filter:')
if 'HTTP_200' in out2:
    print('   200 OK (no filter applied)')
elif 'HTTP_302' in out2:
    print('   302 Redirect (expected without dashboard_id filter)')
else:
    print('   ', out2[:200])

# TEST 3: Native filter POST (unchanged)
_, co3, _ = ssh.exec_command(
    'curl -s -w "\nHTTP_%{http_code}" -X POST http://127.0.0.1:8088/api/v1/chart/data '
    '-H "Content-Type: application/json" '
    '-H "Authorization: Bearer ' + token + '" '
    '-d \'{"datasource":{"id":3,"type":"table"},"queries":[{"columns":["year"],"row_limit":5}]}\''
)
print('\nTEST 3 - Native filter:', 'OK' if 'HTTP_200' in co3.read().decode(errors='replace') else 'FAIL')

ssh.close()
