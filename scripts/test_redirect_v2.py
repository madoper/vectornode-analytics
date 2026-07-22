import paramiko, json

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=10)

# Login
std2 = ssh.exec_command(
    "curl -s -X POST http://127.0.0.1:8088/api/v1/security/login "
    "-H 'Content-Type: application/json' "
    "-d '{\"username\":\"admin\",\"password\":\"admin\",\"provider\":\"db\"}'"
)
token = json.loads(std2[1].read().decode())["access_token"]

# Test POST via Nginx - without following redirect to see what it does
fd = json.dumps({"slice_id": 1})
std4 = ssh.exec_command(
    'curl -s -i -X POST "https://bi.vectornode.ru/api/v1/chart/data?form_data=' + fd + '" '
    '-H "Authorization: Bearer ' + token + '" -k 2>&1 | head -20'
)
resp = std4[1].read().decode(errors='replace').strip()
print('Nginx redirect test:')
lines = resp.split('\n')
for line in lines[:15]:
    print(line[:200])

# Also test with -L to follow redirect
std5 = ssh.exec_command(
    'curl -s -L -X POST "https://bi.vectornode.ru/api/v1/chart/data?form_data=' + fd + '" '
    '-H "Authorization: Bearer ' + token + '" -k --post301 --post302 2>&1 | head -c 300'
)
resp2 = std5[1].read().decode(errors='replace').strip()
print('\nWith redirect follow:')
print(resp2[:300] if resp2 else '(empty)')

ssh.close()
