import paramiko, json
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=10)

# Upload clean config to the ACTIVE file (podft)
sftp = ssh.open_sftp()
sftp.put(r'D:\project\FRS_TEST\nginx\vectornode.conf', '/etc/nginx/sites-available/podft')
sftp.close()
print('Config uploaded to podft')

# Test
_, o, _ = ssh.exec_command('nginx -t 2>&1')
print('nginx -t:', o.read().decode(errors='replace').strip())

# Reload
_, o2, _ = ssh.exec_command('nginx -s reload 2>&1')
print('reload:', o2.read().decode(errors='replace').strip())

# Verify no more chart/data redirect
_, o3, _ = ssh.exec_command('grep -c "chart/data" /etc/nginx/sites-available/podft')
count = o3.read().decode(errors='replace').strip()
print(f'chart/data refs in podft: {count}')

# Test: chart GET
_, auth, _ = ssh.exec_command(
    "curl -s -X POST http://127.0.0.1:8088/api/v1/security/login -H 'Content-Type: application/json' -d '{\"username\":\"admin\",\"password\":\"admin\",\"provider\":\"db\"}'"
)
token = json.loads(auth.read().decode())["access_token"]

for cid in [1, 2, 3, 4]:
    _, o4, _ = ssh.exec_command(
        'curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8088/api/v1/chart/' + str(cid) + '/data/ -H "Authorization: Bearer ' + token + '"'
    )
    print(f'Chart {cid} GET: {o4.read().decode(errors="replace").strip()}')

# Test: native filter POST
_, o5, _ = ssh.exec_command(
    'curl -s -X POST http://127.0.0.1:8088/api/v1/chart/data -H "Content-Type: application/json" '
    '-H "Authorization: Bearer ' + token + '" '
    '-d \'{"datasource":{"id":3,"type":"table"},"queries":[{"columns":["year"],"row_limit":5}]}\' '
    '-w " HTTP_%{http_code}"'
)
print('\nNative filter POST:', o5.read().decode(errors='replace')[:200])

ssh.close()
