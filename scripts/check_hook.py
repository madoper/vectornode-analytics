import paramiko, time, json, urllib.parse
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

# Check for hook message in LATEST logs (only after most recent restart)
_, o, _ = ssh.exec_command(
    'docker logs podft-superset --since 2m 2>&1 | grep -i "hook\|patched\|Traceback\|AttributeError" | head -10'
)
print('Recent logs:')
print(o.read().decode(errors='replace') or 'No matches')

# Test if Superset is up
time.sleep(10)
_, auth, _ = ssh.exec_command(
    'curl -s -X POST http://127.0.0.1:8088/api/v1/security/login -H "Content-Type: application/json" -d \'{"username":"admin","password":"admin","provider":"db"}\''
)
resp = auth.read().decode(errors='replace')
if not resp or not resp.startswith('{'):
    print('Superset not ready yet:', resp[:100])
    ssh.close()
    exit()

token = json.loads(resp)["access_token"]
print('Login OK')

fd = urllib.parse.quote('{"slice_id":5}')
_, o2, _ = ssh.exec_command(
    'curl -s -w "\nHTTP_%{http_code}" -X POST "http://127.0.0.1:8088/api/v1/chart/data?form_data=' + fd + '" '
    '-H "Authorization: Bearer ' + token + '"'
)
print('\nChart POST (query only, no body):')
print(o2.read().decode(errors='replace')[:800])

ssh.close()
