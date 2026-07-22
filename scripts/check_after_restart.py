import paramiko, json
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=10)

# Check container status
_, o, _ = ssh.exec_command('docker ps --filter name=podft-superset --format "{{.Status}}"')
print('Container status:', o.read().decode(errors='replace'))

# Test POST /api/v1/chart/data with native filter query
_, auth, _ = ssh.exec_command(
    'curl -s -X POST http://127.0.0.1:8088/api/v1/security/login -H "Content-Type: application/json" -d \'{"username":"admin","password":"admin","provider":"db"}\''
)
token = json.loads(auth.read().decode())["access_token"]

# Native filter style POST
_, o2, _ = ssh.exec_command(
    'curl -s -w "\nHTTP_%{http_code}" -X POST http://127.0.0.1:8088/api/v1/chart/data '
    '-H "Content-Type: application/json" '
    '-H "Authorization: Bearer ' + token + '" '
    '-d \'{"datasource":{"id":3,"type":"table"},"queries":[{"columns":["year"],"row_limit":10}],"force":false}\''
)
print('\nNative filter POST test:')
print(o2.read().decode(errors='replace')[:500])

# Check nginx access log for recent errors
_, o3, _ = ssh.exec_command(
    'tail -5 /var/log/nginx/access.log | grep "chart/data"'
)
print('\nRecent chart/data requests:')
print(o3.read().decode(errors='replace'))

ssh.close()
