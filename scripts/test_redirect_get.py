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

# Test GET redirect (browser behavior: after 302, browser does GET)
stdin2, stdout2, stderr2 = ssh.exec_command(
    'curl -s -L -o /dev/null -w "%{http_code}" -k --post302 "https://bi.vectornode.ru/api/v1/chart/data?form_data=%7B%22slice_id%22%3A1%7D" '
    '-H "Authorization: Bearer ' + token + '"'
)
print('--post302:', stdout2.read().decode(errors='replace').strip())

# Without -X POST (browser behavior)
stdin3, stdout3, stderr3 = ssh.exec_command(
    'curl -s -L -o /dev/null -w "%{http_code}" -k "https://bi.vectornode.ru/api/v1/chart/data?form_data=%7B%22slice_id%22%3A1%7D" '
    '-H "Authorization: Bearer ' + token + '"'
)
print('No -X POST:', stdout3.read().decode(errors='replace').strip())

# GET the redirect URL directly with auth (what browser would GET after redirect)
stdin4, stdout4, stderr4 = ssh.exec_command(
    'curl -s -o /dev/null -w "%{http_code}" -k "https://bi.vectornode.ru/api/v1/chart/1/data/" '
    '-H "Authorization: Bearer ' + token + '"'
)
print('Direct GET via HTTPS:', stdout4.read().decode(errors='replace').strip())

ssh.close()
