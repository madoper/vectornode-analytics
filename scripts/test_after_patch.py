import paramiko, json, urllib.parse, time
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

# Wait for Superset
time.sleep(10)

# Login
for attempt in range(3):
    _, auth, _ = ssh.exec_command(
        'curl -s -X POST http://127.0.0.1:8088/api/v1/security/login -H "Content-Type: application/json" -d \'{"username":"admin","password":"admin","provider":"db"}\''
    )
    resp = auth.read().decode(errors='replace')
    try:
        token = json.loads(resp)["access_token"]
        print('Login OK')
        break
    except:
        print(f'Attempt {attempt+1}: waiting...')
        time.sleep(5)
else:
    print('Login failed')
    _, o_logs, _ = ssh.exec_command('docker logs podft-superset --tail 20 2>&1')
    print(o_logs.read().decode(errors='replace')[-500:])
    ssh.close()
    exit()

# Test chart POST - no body, just query string
fd = urllib.parse.quote('{"slice_id":5}')
_, o, _ = ssh.exec_command(
    'curl -s -w "\nHTTP_%{http_code}" -X POST "http://127.0.0.1:8088/api/v1/chart/data?form_data=' + fd + '" '
    '-H "Authorization: Bearer ' + token + '"'
)
print('\nChart POST (query string only, no body):')
print(o.read().decode(errors='replace')[:600])

# Check latest log for patched message
_, o2, _ = ssh.exec_command(
    'docker logs podft-superset 2>&1 | grep "patched\|Traceback\|NameError" | tail -5'
)
print('\n\nLatest patch logs:')
print(o2.read().decode(errors='replace'))

ssh.close()
