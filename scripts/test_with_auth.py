import paramiko, json

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=10)

# Login
stdin, stdout, stderr = ssh.exec_command(
    "curl -s -X POST http://127.0.0.1:8088/api/v1/security/login "
    "-H 'Content-Type: application/json' "
    "-d '{\"username\":\"admin\",\"password\":\"admin\",\"provider\":\"db\"}'"
)
token = json.loads(stdout.read().decode())["access_token"]

# Test Nginx HTTPS with auth
stdin2, stdout2, stderr2 = ssh.exec_command(
    'curl -s -k "https://bi.vectornode.ru/api/v1/chart/data?form_data=%7B%22slice_id%22%3A1%7D" '
    '-H "Authorization: Bearer ' + token + '" 2>&1 | head -c 400'
)
resp = stdout2.read().decode(errors='replace').strip()
print('Nginx WITH auth:', resp[:400])

# Also test with slice_id=3
stdin3, stdout3, stderr3 = ssh.exec_command(
    'curl -s -k "https://bi.vectornode.ru/api/v1/chart/data?form_data=%7B%22slice_id%22%3A3%7D" '
    '-H "Authorization: Bearer ' + token + '" 2>&1 | head -c 400'
)
resp2 = stdout3.read().decode(errors='replace').strip()
print('\nChart 3:', resp2[:300])

ssh.close()
