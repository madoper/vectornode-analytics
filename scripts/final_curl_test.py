import paramiko, json

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

# Check current config
stdin, stdout, stderr = ssh.exec_command(
    "sed -n '/location = \\/api\\/v1\\/chart\\/data/,/}/p' /etc/nginx/sites-enabled/vectornode.ru | head -10"
)
print('Config:')
print(stdout.read().decode(errors='replace').strip()[:500])

# Login
stdin2, stdout2, stderr2 = ssh.exec_command(
    "curl -s -X POST http://127.0.0.1:8088/api/v1/security/login "
    "-H 'Content-Type: application/json' "
    "-d '{\"username\":\"admin\",\"password\":\"admin\",\"provider\":\"db\"}'"
)
token = json.loads(stdout2.read().decode())["access_token"]
print(f'\nToken OK')

# Test HTTPS with auth
stdin3, stdout3, stderr3 = ssh.exec_command(
    'curl -s -k "https://bi.vectornode.ru/api/v1/chart/data?form_data=%7B%22slice_id%22%3A1%7D" '
    '-H "Authorization: Bearer ' + token + '" 2>&1 | head -c 400'
)
print(f'\nAuth test: {stdout3.read().decode(errors="replace").strip()[:400]}')

# Test HTTPS without auth
stdin4, stdout4, stderr4 = ssh.exec_command(
    'curl -s -k "https://bi.vectornode.ru/api/v1/chart/data?form_data=%7B%22slice_id%22%3A1%7D" 2>&1 | head -c 400'
)
print(f'\nNo auth: {stdout4.read().decode(errors="replace").strip()[:400]}')

# Test GET directly
stdin5, stdout5, stderr5 = ssh.exec_command(
    'curl -s "http://127.0.0.1:8088/api/v1/chart/1/data/" '
    '-H "Authorization: Bearer ' + token + '" 2>&1 | head -c 300'
)
print(f'\nDirect GET: {stdout5.read().decode(errors="replace").strip()[:200]}')

ssh.close()
