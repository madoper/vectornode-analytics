import paramiko, json
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=10)

_, out_auth, _ = ssh.exec_command(
    "curl -s -X POST http://127.0.0.1:8088/api/v1/security/login -H 'Content-Type: application/json' -d '{\"username\":\"admin\",\"password\":\"admin\",\"provider\":\"db\"}'"
)
token = json.loads(out_auth.read().decode())["access_token"]

# Get full response for chart 4
_, out4, _ = ssh.exec_command(
    f'curl -s "http://127.0.0.1:8088/api/v1/chart/4/data/" -H "Authorization: Bearer {token}"'
)
resp = json.loads(out4.read().decode())
result = resp["result"][0]
print(f"query: {result['query']}")
print(f"colnames: {result.get('colnames', [])}")
print(f"coltypes: {result.get('coltypes', [])}")
print(f"data length: {len(result.get('data', []))}")
print(f"status: {result.get('status')}")
print(f"stacktrace: {result.get('stacktrace', 'none')[:500]}")

ssh.close()
