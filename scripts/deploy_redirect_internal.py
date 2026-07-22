import paramiko, time, json, urllib.parse
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', port=22, username='root', password='8884&JKL%f75', timeout=15)

V = '/var/lib/docker/volumes/podft_superset_data/_data'
sftp = ssh.open_sftp()
sftp.put(r'D:\project\FRS_TEST\scripts\superset_config_clean.py', '/opt/podft/infra/superset-init/superset_config.py')
sftp.put(r'D:\project\FRS_TEST\scripts\superset_config_clean.py', f'{V}/superset_config.py')
sftp.close()

_, so, _ = ssh.exec_command('docker restart podft-superset')
print('Restarting...')
time.sleep(35)

# Login
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

# Test chart POST with slice_id → should get 302 redirect internally
fd = urllib.parse.quote('{"slice_id":5}')
_, co, _ = ssh.exec_command(
    'curl -s -w "\nHTTP_%{http_code}" -X POST "http://127.0.0.1:8088/api/v1/chart/data?form_data=' + fd + '" '
    '-H "Content-Type: application/json" '
    '-H "Authorization: Bearer ' + token + '"'
)
out = co.read().decode(errors='replace')
print('\nChart POST (slice_id only):')
if 'HTTP_200' in out:
    print('   SUCCESS!')
    if '"query"' in out:
        idx = out.index('"query"')
        print('   Query:', out[idx:idx+200])
elif 'Redirecting' in out or '302' in out:
    print('   Redirecting - middleware working as expected')
elif 'HTTP_400' in out:
    print('   FAIL:', out[:200])
else:
    print('   ', out[:300])

# Test with full form_data (no slice_id) → should pass through
_, co2, _ = ssh.exec_command(
    'curl -s -w "\nHTTP_%{http_code}" -X POST "http://127.0.0.1:8088/api/v1/chart/data?form_data=' + urllib.parse.quote('{"datasource":"3__table","queries":[{"columns":["year"]}]}') + '" '
    '-H "Content-Type: application/json" '
    '-H "Authorization: Bearer ' + token + '"'
)
out2 = co2.read().decode(errors='replace')
print('\nChart POST (full form_data):', 'OK' if 'HTTP_200' in out2 else out2[:150])

# Test native filter (no form_data in query) → should pass through
_, co3, _ = ssh.exec_command(
    'curl -s -w "\nHTTP_%{http_code}" -X POST http://127.0.0.1:8088/api/v1/chart/data '
    '-H "Content-Type: application/json" '
    '-H "Authorization: Bearer ' + token + '" '
    '-d \'{"datasource":{"id":3,"type":"table"},"queries":[{"columns":["year"],"row_limit":5}]}\''
)
print('\nNative filter:', 'OK' if 'HTTP_200' in co3.read().decode(errors='replace') else 'FAIL')

ssh.close()
