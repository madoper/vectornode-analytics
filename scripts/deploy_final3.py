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

# Test redirect URL
_, auth, _ = ssh.exec_command(
    'curl -s -X POST http://127.0.0.1:8088/api/v1/security/login -H "Content-Type: application/json" -d \'{"username":"admin","password":"admin","provider":"db"}\''
)
token = json.loads(auth.read().decode())["access_token"]

# Test encoded
fd = urllib.parse.quote('{"slice_id":5}')
url = 'https://127.0.0.1/api/v1/chart/data?form_data=' + fd + '&dashboard_id=2'

_, o3, _ = ssh.exec_command(
    'curl -s -k -w "REDIR=%{redirect_url}" -X POST "' + url + '" '
    '-H "Host: bi.vectornode.ru" '
    '-H "Authorization: Bearer ' + token + '"'
)
print('Encoded redirect:', o3.read().decode(errors='replace')[:200])

# Test unencoded
fd2 = '{"slice_id":5}'
url2 = 'https://127.0.0.1/api/v1/chart/data?form_data=' + fd2 + '&dashboard_id=2'

_, o4, _ = ssh.exec_command(
    'curl -s -k -w "REDIR=%{redirect_url}" -X POST "' + url2 + '" '
    '-H "Host: bi.vectornode.ru" '
    '-H "Authorization: Bearer ' + token + '"'
)
print('\nUnencoded redirect:', o4.read().decode(errors='replace')[:200])

ssh.close()
