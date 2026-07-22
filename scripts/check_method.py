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

# Test GET directly with auth
stdin2, stdout2, stderr2 = ssh.exec_command(
    'curl -s -o /dev/null -w "%{http_code}" "http://127.0.0.1:8088/api/v1/chart/1/data/" '
    '-H "Authorization: Bearer ' + token + '"'
)
print('GET /chart/1/data/:', stdout2.read().decode(errors='replace').strip())

# Test POST directly to the same URL (should fail)
stdin3, stdout3, stderr3 = ssh.exec_command(
    'curl -s -o /dev/null -w "%{http_code}" -X POST "http://127.0.0.1:8088/api/v1/chart/1/data/" '
    '-H "Authorization: Bearer ' + token + '"'
)
print('POST /chart/1/data/:', stdout3.read().decode(errors='replace').strip())

# Test POST to chart/data via Nginx (should be proxied as GET)
stdin4, stdout4, stderr4 = ssh.exec_command(
    'curl -s -o /dev/null -w "%{http_code}" -k -X POST "https://bi.vectornode.ru/api/v1/chart/data?form_data=%7B%22slice_id%22%3A1%7D" '
    '-H "Authorization: Bearer ' + token + '"'
)
print('Nginx POST:', stdout4.read().decode(errors='replace').strip())

ssh.close()
