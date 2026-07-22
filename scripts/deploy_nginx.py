import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=10)

# Upload new nginx config
sftp = ssh.open_sftp()
sftp.put(r'D:\project\FRS_TEST\nginx\vectornode.conf', '/etc/nginx/sites-available/vectornode.ru')
sftp.close()
print('Config uploaded')

# Test nginx config
_, o, _ = ssh.exec_command('nginx -t 2>&1')
print('nginx -t:')
print(o.read().decode(errors='replace'))

# Reload
_, o2, _ = ssh.exec_command('nginx -s reload 2>&1')
print('reload:')
print(o2.read().decode(errors='replace'))

# Test: native filter POST without slice_id
import json
_, out_auth, _ = ssh.exec_command(
    "curl -s -X POST http://127.0.0.1:8088/api/v1/security/login -H 'Content-Type: application/json' -d '{\"username\":\"admin\",\"password\":\"admin\",\"provider\":\"db\"}'"
)
token = json.loads(out_auth.read().decode())["access_token"]

# POST without slice_id (simulates native filter query)
_, o3, _ = ssh.exec_command(
    'curl -s -w " HTTP_%{http_code}" -X POST "http://127.0.0.1:8088/api/v1/chart/data" '
    '-H "Content-Type: application/json" '
    '-H "Authorization: Bearer ' + token + '" '
    '-d \'{"datasource":{"id":3,"type":"table"},"queries":[{"columns":["year"],"row_limit":10}]}\''
)
out = o3.read().decode(errors='replace')
print(f'\nNative filter test (no slice_id): {out[:200]}')

ssh.close()
