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

# Test direct GET with auth
stdin2, stdout2, stderr2 = ssh.exec_command(
    'curl -s "http://127.0.0.1:8088/api/v1/chart/1/data/" '
    '-H "Authorization: Bearer ' + token + '" 2>&1 | head -c 300'
)
print('Direct GET:', stdout2.read().decode(errors='replace').strip()[:300])

# Test direct GET without auth
stdin3, stdout3, stderr3 = ssh.exec_command(
    'curl -s "http://127.0.0.1:8088/api/v1/chart/1/data/" 2>&1 | head -c 200'
)
print('Direct GET noauth:', stdout3.read().decode(errors='replace').strip()[:200])

# Test debug return via Nginx to confirm proxy_pass URL
stdin4, stdout4, stderr4 = ssh.exec_command(
    'curl -s -k "https://bi.vectornode.ru/api/v1/chart/data?form_data=%7B%22slice_id%22%3A1%7D" 2>&1 | head -c 200'
)
print('Nginx noauth:', stdout4.read().decode(errors='replace').strip()[:200])

ssh.close()
