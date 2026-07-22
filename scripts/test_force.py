import paramiko, time, json, urllib.parse
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', port=22, username='root', password='8884&JKL%f75', timeout=10)

# Login
_, auth, _ = ssh.exec_command(
    'curl -s -X POST http://127.0.0.1:8088/api/v1/security/login -H "Content-Type: application/json" -d \'{"username":"admin","password":"admin","provider":"db"}\''
)
token = json.loads(auth.read().decode(errors='replace'))["access_token"]

# Test with force=true to bypass cache
fd = urllib.parse.quote('{"slice_id":4}')
_, co, _ = ssh.exec_command(
    'curl -s -w "\nHTTP_%{http_code}" -X POST "http://127.0.0.1:8088/api/v1/chart/data?form_data=' + fd + '&dashboard_id=2" '
    '-H "Content-Type: application/json" '
    '-H "Authorization: Bearer ' + token + '" '
    '-H "Referer: https://bi.vectornode.ru/superset/dashboard/vectornode-anomalies/?native_filters_key=on3j7Uo8xSs" '
    '-d \'{"force":true}\''
)
out = co.read().decode(errors='replace')
print('With force=true:', out[:600])

# Check debug
_, so2, _ = ssh.exec_command('docker logs podft-superset --since 30s 2>&1 | grep "FILTER_" | tail -5')
print('\nDebug:', so2.read().decode(errors='replace') or 'NONE')

ssh.close()
