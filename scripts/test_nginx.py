import paramiko, json, urllib.parse
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=10)

# Login via Superset directly
_, auth, _ = ssh.exec_command(
    'curl -s -X POST http://127.0.0.1:8088/api/v1/security/login -H "Content-Type: application/json" -d \'{"username":"admin","password":"admin","provider":"db"}\''
)
token = json.loads(auth.read().decode())["access_token"]

# Test through Nginx on port 80
fd = urllib.parse.quote('{"slice_id":5}')
url = 'http://127.0.0.1/api/v1/chart/data?form_data=' + fd + '&dashboard_id=2'

_, o, _ = ssh.exec_command(
    'curl -s -L -w "\nHTTP_%{http_code}" -X POST "' + url + '" '
    '-H "Host: bi.vectornode.ru" '
    '-H "Authorization: Bearer ' + token + '"'
)
print('Chart POST through Nginx:')
print(o.read().decode(errors='replace')[:500])

# Native filter through Nginx
_, o2, _ = ssh.exec_command(
    'curl -s -L -w "\nHTTP_%{http_code}" -X POST http://127.0.0.1/api/v1/chart/data '
    '-H "Host: bi.vectornode.ru" '
    '-H "Content-Type: application/json" '
    '-H "Authorization: Bearer ' + token + '" '
    '-d \'{"datasource":{"id":3,"type":"table"},"queries":[{"columns":["year"],"row_limit":5}]}\''
)
print('\n\nNative filter POST through Nginx:')
print(o2.read().decode(errors='replace')[:500])

ssh.close()
