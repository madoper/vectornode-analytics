import paramiko, json, urllib.parse

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

# Login
stdin, stdout, stderr = ssh.exec_command(
    "curl -s -X POST http://127.0.0.1:8088/api/v1/security/login "
    "-H 'Content-Type: application/json' "
    "-d '{\"username\":\"admin\",\"password\":\"admin\",\"provider\":\"db\"}'"
)
token = json.loads(stdout.read().decode())["access_token"]

# Test HTTPS POST directly
fd = urllib.parse.quote(json.dumps({"slice_id": 1}))
stdin2, stdout2, stderr2 = ssh.exec_command(
    f'curl -s -i -k -X POST "https://bi.vectornode.ru/api/v1/chart/data?form_data={fd}" '
    f'-H "Authorization: Bearer {token}" 2>&1 | head -20'
)
print('HTTPS POST test:')
resp = stdout2.read().decode(errors='replace').strip()
lines = resp.split('\n')
for line in lines[:12]:
    print(line[:200])

# Also test HTTPS GET with the rewrite
stdin3, stdout3, stderr3 = ssh.exec_command(
    f'curl -s -i -k "https://bi.vectornode.ru/api/v1/chart/data?form_data={fd}" '
    f'-H "Authorization: Bearer {token}" 2>&1 | head -20'
)
print('\nHTTPS GET test:')
resp2 = stdout3.read().decode(errors='replace').strip()
for line in resp2.split('\n')[:12]:
    print(line[:200])

ssh.close()
