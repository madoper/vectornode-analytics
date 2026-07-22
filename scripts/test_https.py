import paramiko, json

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=10)

# Test via HTTPS
stdin, stdout, stderr = ssh.exec_command(
    'curl -s -i -k -X POST "https://bi.vectornode.ru/api/v1/chart/data?form_data={%22slice_id%22:1}" 2>&1 | head -15'
)
print('HTTPS response:')
resp = stdout.read().decode(errors='replace').strip()
for line in resp.split('\n')[:12]:
    print(line[:200])

# Login for test
stdin2, stdout2, stderr2 = ssh.exec_command(
    "curl -s -X POST http://127.0.0.1:8088/api/v1/security/login "
    "-H 'Content-Type: application/json' "
    "-d '{\"username\":\"admin\",\"password\":\"admin\",\"provider\":\"db\"}'"
)
token = json.loads(stdout2.read().decode())["access_token"]

# Test via Nginx with auth
fd = json.dumps({"slice_id": 1})
stdin3, stdout3, stderr3 = ssh.exec_command(
    'curl -s -i -k -X POST "https://bi.vectornode.ru/api/v1/chart/data?form_data=' + fd + '" '
    '-H "Authorization: Bearer ' + token + '" 2>&1 | head -15'
)
print('\nWith auth:')
resp2 = stdout3.read().decode(errors='replace').strip()
for line in resp2.split('\n')[:12]:
    print(line[:200])

# Test GET directly
stdin4, stdout4, stderr4 = ssh.exec_command(
    'curl -s -o /dev/null -w "%{http_code}" "http://127.0.0.1:8088/api/v1/chart/1/data/" '
    '-H "Authorization: Bearer ' + token + '"'
)
print(f'\nDirect GET: {stdout4.read().decode(errors="replace").strip()}')

ssh.close()
