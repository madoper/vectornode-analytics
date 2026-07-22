import paramiko, json

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=10)

# Login
_, stdout2, _ = ssh.exec_command(
    "curl -s -X POST http://127.0.0.1:8088/api/v1/security/login "
    "-H 'Content-Type: application/json' "
    "-d '{\"username\":\"admin\",\"password\":\"admin\",\"provider\":\"db\"}'"
)
token = json.loads(stdout2.read().decode())["access_token"]

# Test GET for each chart
for cid in [1, 2, 3, 4, 5, 6]:
    _, stdout3, _ = ssh.exec_command(
        'curl -s -w " HTTP_%{http_code}" "http://127.0.0.1:8088/api/v1/chart/' + str(cid) + '/data/" '
        '-H "Authorization: Bearer ' + token + '" 2>&1'
    )
    out = stdout3.read().decode(errors='replace').strip()
    print(f'Chart {cid}: {out[:300]}')

ssh.close()
