import paramiko, time, json, urllib.parse
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=10)

# Simplify fix_chart_patch.py to no-op
V = '/var/lib/docker/volumes/podft_superset_data/_data'
sftp = ssh.open_sftp()
f = sftp.file(f'{V}/fix_chart_patch.py', 'w')
f.write('"""No-op — middleware handles form_data inject now."""\ndef init():\n    print("fix_chart_patch: no-op", flush=True)\n')
f.close()
sftp.close()

# Restart
_, o, _ = ssh.exec_command('docker restart podft-superset')
print('Restarting...')
time.sleep(25)

# Check for errors
_, o2, _ = ssh.exec_command('docker logs podft-superset --since 1m 2>&1 | grep -i "Error\|Traceback\|no-op\|FormData" | tail -5')
print('Logs:', o2.read().decode(errors='replace') or 'CLEAN')

# Test
time.sleep(10)
_, auth, _ = ssh.exec_command(
    'curl -s -X POST http://127.0.0.1:8088/api/v1/security/login -H "Content-Type: application/json" -d \'{"username":"admin","password":"admin","provider":"db"}\''
)
resp = auth.read().decode(errors='replace')
token = json.loads(resp)["access_token"] if resp.startswith('{') else None
if not token:
    print('Login failed:', resp[:100])
    print('Retrying...')
    time.sleep(10)
    _, auth2, _ = ssh.exec_command(
        'curl -s -X POST http://127.0.0.1:8088/api/v1/security/login -H "Content-Type: application/json" -d \'{"username":"admin","password":"admin","provider":"db"}\''
    )
    resp2 = auth2.read().decode(errors='replace')
    token = json.loads(resp2)["access_token"] if resp2.startswith('{') else None

if not token:
    print('Giving up')
    ssh.close()
    exit()

print('Login OK')

# Test chart POST
fd = urllib.parse.quote('{"slice_id":5}')
_, o3, _ = ssh.exec_command(
    'curl -s -w "\nHTTP_%{http_code}" -X POST "http://127.0.0.1:8088/api/v1/chart/data?form_data=' + fd + '" '
    '-H "Authorization: Bearer ' + token + '"'
)
print('\nChart POST:', o3.read().decode(errors='replace')[:600])

# Test native filter POST
_, o4, _ = ssh.exec_command(
    'curl -s -w "\nHTTP_%{http_code}" -X POST http://127.0.0.1:8088/api/v1/chart/data '
    '-H "Content-Type: application/json" '
    '-H "Authorization: Bearer ' + token + '" '
    '-d \'{"datasource":{"id":3,"type":"table"},"queries":[{"columns":["year"],"row_limit":5}]}\''
)
print('\nNative filter:', o4.read().decode(errors='replace')[:300])

ssh.close()
