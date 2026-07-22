import paramiko, json, urllib.parse
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=10)

# Upload
sftp = ssh.open_sftp()
sftp.put(r'D:\project\FRS_TEST\nginx\vectornode.conf', '/etc/nginx/sites-available/podft')
sftp.close()

_, o, _ = ssh.exec_command('nginx -t 2>&1')
print('nginx -t:', o.read().decode(errors='replace').strip())

_, o2, _ = ssh.exec_command('nginx -s reload 2>&1')
print('reload:', o2.read().decode(errors='replace').strip())

# Test
_, auth, _ = ssh.exec_command(
    'curl -s -X POST http://127.0.0.1:8088/api/v1/security/login -H "Content-Type: application/json" -d \'{"username":"admin","password":"admin","provider":"db"}\''
)
token = json.loads(auth.read().decode())["access_token"]

# Test with URL-encoded form_data (like the browser)
fd = urllib.parse.quote('{"slice_id":5}')
url = 'https://127.0.0.1/api/v1/chart/data?form_data=' + fd + '&dashboard_id=2'

_, o3, _ = ssh.exec_command(
    'curl -s -k -L -w "\nHTTP_%{http_code}" -X POST "' + url + '" '
    '-H "Host: bi.vectornode.ru" '
    '-H "Content-Type: application/json" '
    '-H "Authorization: Bearer ' + token + '"'
)
print('\nChart POST (URL-encoded, follow redirect):')
out = o3.read().decode(errors='replace')
print(out[:600])

# Also test with unencoded
fd2 = '{"slice_id":5}'
url2 = 'https://127.0.0.1/api/v1/chart/data?form_data=' + fd2 + '&dashboard_id=2'

_, o4, _ = ssh.exec_command(
    'curl -s -k -L -w "\nHTTP_%{http_code}" -X POST "' + url2 + '" '
    '-H "Host: bi.vectornode.ru" '
    '-H "Content-Type: application/json" '
    '-H "Authorization: Bearer ' + token + '"'
)
print('\nChart POST (unencoded, follow redirect):')
print(o4.read().decode(errors='replace')[:600])

# Native filter test
_, o5, _ = ssh.exec_command(
    'curl -s -k -L -w "\nHTTP_%{http_code}" -X POST https://127.0.0.1/api/v1/chart/data '
    '-H "Host: bi.vectornode.ru" '
    '-H "Content-Type: application/json" '
    '-H "Authorization: Bearer ' + token + '" '
    '-d \'{"datasource":{"id":3,"type":"table"},"queries":[{"columns":["year"],"row_limit":5}]}\''
)
print('\n\nNative filter POST:')
print(o5.read().decode(errors='replace')[:400])

ssh.close()
