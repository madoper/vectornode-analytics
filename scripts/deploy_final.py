import paramiko, json, urllib.parse
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=10)

# Upload to podft (active config)
sftp = ssh.open_sftp()
sftp.put(r'D:\project\FRS_TEST\nginx\vectornode.conf', '/etc/nginx/sites-available/podft')
sftp.close()

# Also upload as vectornode.ru for reference
ssh.exec_command('cp /etc/nginx/sites-available/podft /etc/nginx/sites-available/vectornode.ru')
print('Config uploaded')

# Test and reload
_, o, _ = ssh.exec_command('nginx -t 2>&1')
print('nginx -t:', o.read().decode(errors='replace').strip())

_, o2, _ = ssh.exec_command('nginx -s reload 2>&1')
print('reload:', o2.read().decode(errors='replace').strip())

# Test
_, auth, _ = ssh.exec_command(
    "curl -s -X POST http://127.0.0.1:8088/api/v1/security/login -H 'Content-Type: application/json' -d '{\"username\":\"admin\",\"password\":\"admin\",\"provider\":\"db\"}'"
)
token = json.loads(auth.read().decode())["access_token"]

# Test 1: Chart render POST (with slice_id) - should get 302
fd = urllib.parse.quote('{"slice_id":5}')
url = f'http://127.0.0.1:8088/api/v1/chart/data?form_data={fd}&dashboard_id=2'
_, o3, _ = ssh.exec_command(
    f'curl -s -o /dev/null -w "%{{http_code}}" -X POST "{url}" -H "Authorization: Bearer {token}"'
)
print(f'\nChart POST (slice_id=5): HTTP {o3.read().decode(errors="replace").strip()}')

# Test 2: Native filter POST (no slice_id) - should pass through
_, o4, _ = ssh.exec_command(
    'curl -s -o /dev/null -w "%{http_code}" -X POST http://127.0.0.1:8088/api/v1/chart/data '
    '-H "Content-Type: application/json" '
    '-H "Authorization: Bearer ' + token + '" '
    '-d \'{"datasource":{"id":3,"type":"table"},"queries":[{"columns":["year"],"row_limit":5}]}\''
)
print(f'Native filter POST: HTTP {o4.read().decode(errors="replace").strip()}')

ssh.close()
