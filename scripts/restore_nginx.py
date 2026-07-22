import paramiko, json, urllib.parse
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=10)

# Upload correct config
sftp = ssh.open_sftp()
sftp.put(r'D:\project\FRS_TEST\nginx\vectornode.conf', '/etc/nginx/sites-available/podft')
sftp.close()

# Test & reload
_, o, _ = ssh.exec_command('nginx -t 2>&1')
print('nginx -t:', o.read().decode(errors='replace').strip())

_, o2, _ = ssh.exec_command('nginx -s reload 2>&1')
print('reload:', o2.read().decode(errors='replace').strip())

# Test: Chart POST (encoded) -> should get 302
_, auth, _ = ssh.exec_command(
    'curl -s -X POST http://127.0.0.1:8088/api/v1/security/login -H "Content-Type: application/json" -d \'{"username":"admin","password":"admin","provider":"db"}\''
)
token = json.loads(auth.read().decode())["access_token"]

fd = urllib.parse.quote('{"slice_id":5}')
_, o3, _ = ssh.exec_command(
    'curl -s -k -D - -o /dev/null -X POST "https://bi.vectornode.ru/api/v1/chart/data?form_data=' + fd + '" '
    '-H "Authorization: Bearer ' + token + '"'
)
headers = o3.read().decode(errors='replace')
print('\nChart POST redirect:', headers.strip()[:200])

# Test: Native filter POST
_, o4, _ = ssh.exec_command(
    'curl -s -k -w "\nHTTP_%{http_code}" -X POST https://bi.vectornode.ru/api/v1/chart/data '
    '-H "Content-Type: application/json" '
    '-H "Authorization: Bearer ' + token + '" '
    '-d \'{"datasource":{"id":3,"type":"table"},"queries":[{"columns":["year"],"row_limit":5}]}\''
)
print('\nNative filter POST:', o4.read().decode(errors='replace')[:300])

ssh.close()
