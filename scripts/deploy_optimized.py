import paramiko, time, json, urllib.parse
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', port=22, username='root', password='8884&JKL%f75', timeout=15)

V = '/var/lib/docker/volumes/podft_superset_data/_data'
sftp = ssh.open_sftp()
sftp.put(r'D:\project\FRS_TEST\scripts\superset_config_clean.py', '/opt/podft/infra/superset-init/superset_config.py')
sftp.put(r'D:\project\FRS_TEST\scripts\superset_config_clean.py', f'{V}/superset_config.py')
sftp.close()
ssh.exec_command(f'find {V} -name "*.pyc" -delete; find {V} -name "__pycache__" -exec rm -rf {{}} +')

_, so, _ = ssh.exec_command('docker restart podft-superset')
print('Restarting...')
time.sleep(45)

# Check status
_, so2, _ = ssh.exec_command('docker ps --filter name=podft-superset --format "{{.Status}}"')
status = so2.read().decode(errors='replace').strip()
print(f'Status: {status}')

# Check errors
_, so3, _ = ssh.exec_command(
    'docker logs podft-superset --since 20s 2>&1 | grep -iE "traceback|pool|error.*init" | head -5'
)
errs = so3.read().decode(errors='replace').strip()
print(f'Errors: {errs or "NONE"}')

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

# Test chart POST with filter
import time as t
start = t.time()
for i in range(6):
    fd = urllib.parse.quote(f'{{"slice_id":{i+1}}}')
    _, co, _ = ssh.exec_command(
        'curl -s -w "%{http_code}" -X POST "http://127.0.0.1:8088/api/v1/chart/data?form_data=' + fd + '&dashboard_id=2" '
        '-H "Content-Type: application/json" '
        '-H "Authorization: Bearer ' + token + '" '
        '-H "Referer: https://bi.vectornode.ru/superset/dashboard/vectornode-anomalies/?native_filters_key=on3j7Uo8xSs" '
        '-o /dev/null'
    )
    code = co.read().decode(errors='replace').strip()
    print(f'  Chart {i+1}: HTTP {code}', end='')
    if i < 5: print()

elapsed = t.time() - start
print(f'\nTotal: {elapsed:.2f}s for 6 charts ({elapsed/6:.2f}s per chart)')

# Test native filter
_, co7, _ = ssh.exec_command(
    'curl -s -o /dev/null -w "%{http_code}" -X POST http://127.0.0.1:8088/api/v1/chart/data '
    '-H "Content-Type: application/json" '
    '-H "Authorization: Bearer ' + token + '" '
    '-d \'{"datasource":{"id":3,"type":"table"},"queries":[{"columns":["year"],"row_limit":5}]}\''
)
print(f'Native filter: HTTP {co7.read().decode(errors="replace").strip()}')

# Check pg connections
_, so4, _ = ssh.exec_command(
    "docker exec podft-postgres psql -U podft -d superset -t -A -c "
    "\"SELECT count(*) FROM pg_stat_activity WHERE datname = 'superset'\""
)
print(f'PG connections: {so4.read().decode(errors="replace").strip()}')

ssh.close()
