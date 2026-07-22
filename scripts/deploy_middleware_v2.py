import paramiko, time, json, urllib.parse
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', port=22, username='root', password='8884&JKL%f75', timeout=15)

# 1. Deploy config to both host and volume
V = '/var/lib/docker/volumes/podft_superset_data/_data'
sftp = ssh.open_sftp()
sftp.put(r'D:\project\FRS_TEST\scripts\superset_config_clean.py', '/opt/podft/infra/superset-init/superset_config.py')
sftp.put(r'D:\project\FRS_TEST\scripts\superset_config_clean.py', f'{V}/superset_config.py')
sftp.close()
print('1. Config deployed to host + volume')

# 2. Restart
_, so, _ = ssh.exec_command('docker restart podft-superset')
print('2. Restarting...')
time.sleep(30)

# 3. Check status and errors
_, so2, _ = ssh.exec_command('docker ps --filter name=podft-superset --format "{{.Status}}"')
print('3. Status:', so2.read().decode(errors='replace').strip())

_, so3, _ = ssh.exec_command(
    'docker logs podft-superset --since 30s 2>&1 | grep -iE "syntax|FormData|middleware|ADDITIONAL|traceback" | tail -5'
)
print('   Logs:', so3.read().decode(errors='replace').strip()[:200] or 'CLEAN')

# 4. Test
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

print('   Login OK')

# Chart POST (query only, no body) - the critical test
fd = urllib.parse.quote('{"slice_id":5}')
_, co, _ = ssh.exec_command(
    'curl -s -w "\nHTTP_%{http_code}" -X POST "http://127.0.0.1:8088/api/v1/chart/data?form_data=' + fd + '" '
    '-H "Content-Type: application/json" '
    '-H "Authorization: Bearer ' + token + '"'
)
out = co.read().decode(errors='replace')
print('\n4. Chart POST (query only):')
if 'HTTP_200' in out:
    print('   SUCCESS! Charts work without redirect!')
    print('   Query:', out.split('"query": "')[1][:100] if '"query": "' in out else '')
else:
    print('  ', out[:300])

# Native filter
_, co2, _ = ssh.exec_command(
    'curl -s -w "\nHTTP_%{http_code}" -X POST http://127.0.0.1:8088/api/v1/chart/data '
    '-H "Content-Type: application/json" '
    '-H "Authorization: Bearer ' + token + '" '
    '-d \'{"datasource":{"id":3,"type":"table"},"queries":[{"columns":["year"],"row_limit":5}]}\''
)
out2 = co2.read().decode(errors='replace')
print('\n5. Native filter POST:', 'OK' if 'HTTP_200' in out2 else 'FAIL')

ssh.close()
