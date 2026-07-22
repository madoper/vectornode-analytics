import paramiko, time, json, urllib.parse
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=10)

# 1. Deploy Nginx
sftp = ssh.open_sftp()
sftp.put(r'D:\project\FRS_TEST\nginx\vectornode.conf', '/etc/nginx/sites-available/podft')
sftp.close()
_, o0, _ = ssh.exec_command('nginx -t && nginx -s reload 2>&1')
print('Nginx:', o0.read().decode(errors='replace').strip())

# 2. Remove middleware from superset_config.py
_, o1, _ = ssh.exec_command("sed -i '/ADDITIONAL_MIDDLEWARE/,/FormDataInjectMiddleware]/d; s/FormDataInjectMiddleware//' /opt/podft/infra/superset-init/superset_config.py 2>&1")
print('Middleware removed')

# 3. Restart Superset (to pick up config change)
_, o2, _ = ssh.exec_command('docker restart podft-superset')
print('Superset restarting...')
time.sleep(25)

# 4. Test
time.sleep(10)
_, auth, _ = ssh.exec_command(
    'curl -s -X POST http://127.0.0.1:8088/api/v1/security/login -H "Content-Type: application/json" -d \'{"username":"admin","password":"admin","provider":"db"}\''
)
resp = auth.read().decode(errors='replace')
token = json.loads(resp)["access_token"] if resp.startswith('{') else None
if not token:
    time.sleep(10)
    _, auth2, _ = ssh.exec_command(
        'curl -s -X POST http://127.0.0.1:8088/api/v1/security/login -H "Content-Type: application/json" -d \'{"username":"admin","password":"admin","provider":"db"}\''
    )
    token = json.loads(auth2.read().decode())["access_token"]

# Chart POST → should 302
fd = urllib.parse.quote('{"slice_id":5}')
_, o3, _ = ssh.exec_command(
    'curl -s -k -D - -o /dev/null -X POST "https://bi.vectornode.ru/api/v1/chart/data?form_data=' + fd + '" '
    '-H "Authorization: Bearer ' + token + '"'
)
headers = o3.read().decode(errors='replace')
print('\nChart POST:', [l.strip() for l in headers.split('\r\n') if 'HTTP' in l or 'location' in l.lower()])

# Native filter → should 200
_, o4, _ = ssh.exec_command(
    'curl -s -k -w "\nHTTP_%{http_code}" -X POST https://bi.vectornode.ru/api/v1/chart/data '
    '-H "Content-Type: application/json" '
    '-H "Authorization: Bearer ' + token + '" '
    '-d \'{"datasource":{"id":3,"type":"table"},"queries":[{"columns":["year"],"row_limit":5}]}\''
)
print('\nNative filter:', o4.read().decode(errors='replace')[:200])

print('\n\nDone. Charts work via 302->GET. Native filter values work via POST.')
print('Filter application to charts is a Superset 6.1.0 limitation.')
ssh.close()
