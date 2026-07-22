import paramiko, json, urllib.parse, time
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

# Wait for Superset
time.sleep(5)

# Test: chart POST with form_data only in query string
_, auth, _ = ssh.exec_command(
    'curl -s -X POST http://127.0.0.1:8088/api/v1/security/login -H "Content-Type: application/json" -d \'{"username":"admin","password":"admin","provider":"db"}\''
)
resp = auth.read().decode(errors='replace')
try:
    token = json.loads(resp)["access_token"]
    print('Login OK')
except:
    print('Login failed:', resp[:200])
    token = None

if token:
    fd = urllib.parse.quote('{"slice_id":5}')
    url = 'http://127.0.0.1:8088/api/v1/chart/data?form_data=' + fd + '&dashboard_id=2'
    
    # Test without body (simulating what SPA does)
    _, o, _ = ssh.exec_command(
        'curl -s -w "\nHTTP_%{http_code}" -X POST "' + url + '" '
        '-H "Authorization: Bearer ' + token + '"'
    )
    print('\nChart POST (no body, query only):')
    out = o.read().decode(errors='replace')
    print(out[:600])

    # Test with JSON body
    _, o2, _ = ssh.exec_command(
        'curl -s -w "\nHTTP_%{http_code}" -X POST "' + url + '" '
        '-H "Content-Type: application/json" '
        '-H "Authorization: Bearer ' + token + '" '
        '-d \'{"datasource":{"id":3,"type":"table"},"queries":[{"groupby":["criticality"],"metrics":[{"aggregate":"COUNT","column":{"column_name":"company_id"}}]}]}\''
    )
    print('\nChart POST (with body):')
    print(o2.read().decode(errors='replace')[:400])

# Check error logs
_, o3, _ = ssh.exec_command(
    'docker logs podft-superset 2>&1 | grep -i "patched\\|ChartData\\|data.*api\\|fix_chart" | tail -10'
)
print('\n\nPatch related logs:')
print(o3.read().decode(errors='replace'))

ssh.close()
