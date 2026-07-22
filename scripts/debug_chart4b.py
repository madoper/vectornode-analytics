import paramiko, json
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=10)

# Login
_, o, _ = ssh.exec_command(
    "curl -s -X POST http://127.0.0.1:8088/api/v1/security/login -H \"Content-Type: application/json\" -d '{\"username\":\"admin\",\"password\":\"admin\",\"provider\":\"db\"}'"
)
token = json.loads(o.read().decode())["access_token"]

# Chart 4 data
_, o2, _ = ssh.exec_command(
    f'curl -s "http://127.0.0.1:8088/api/v1/chart/4/data/" -H "Authorization: Bearer {token}"'
)
resp = json.loads(o2.read().decode())
print(json.dumps(resp, indent=2, ensure_ascii=False)[:3000])

ssh.close()
