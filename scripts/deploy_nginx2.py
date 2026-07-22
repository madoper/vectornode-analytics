import paramiko, json
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=10)

# Upload new nginx config
sftp = ssh.open_sftp()
sftp.put(r'D:\project\FRS_TEST\nginx\vectornode.conf', '/etc/nginx/sites-available/vectornode.ru')
sftp.close()
print('Uploaded')

# Test and reload
_, o, _ = ssh.exec_command('nginx -t 2>&1')
print('nginx -t:', o.read().decode(errors='replace').strip())

_, o2, _ = ssh.exec_command('nginx -s reload 2>&1')
print('reload:', o2.read().decode(errors='replace').strip())

# Test: chart GET (should still work)
_, auth, _ = ssh.exec_command(
    "curl -s -X POST http://127.0.0.1:8088/api/v1/security/login -H 'Content-Type: application/json' -d '{\"username\":\"admin\",\"password\":\"admin\",\"provider\":\"db\"}'"
)
token = json.loads(auth.read().decode())["access_token"]

print('\n--- Chart GET test ---')
for cid in [1, 2, 3, 4, 5, 6]:
    _, o3, _ = ssh.exec_command(
        'curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8088/api/v1/chart/' + str(cid) + '/data/ -H "Authorization: Bearer ' + token + '"'
    )
    print(f'Chart {cid}: {o3.read().decode(errors="replace").strip()}')

# Test: native filter POST (no slice_id)
print('\n--- Native filter POST test ---')
_, o4, _ = ssh.exec_command(
    'curl -s -w " HTTP_%{http_code}" -X POST "http://127.0.0.1:8088/api/v1/chart/data" '
    '-H "Content-Type: application/json" '
    '-H "Authorization: Bearer ' + token + '" '
    '-d \'{"datasource":{"id":3,"type":"table"},"queries":[{"columns":["year"],"row_limit":5}]}\''
)
out = o4.read().decode(errors='replace')
print(out[:300])

ssh.close()
