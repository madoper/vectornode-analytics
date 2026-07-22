import paramiko, json, urllib.parse
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=10)

# Login
_, auth, _ = ssh.exec_command(
    "curl -s -X POST http://127.0.0.1:8088/api/v1/security/login -H 'Content-Type: application/json' -d '{\"username\":\"admin\",\"password\":\"admin\",\"provider\":\"db\"}'"
)
token = json.loads(auth.read().decode())["access_token"]

# Test: POST with form_data query param (like the SPA does)
form_data = urllib.parse.quote('{"slice_id":5}')
url = f'http://127.0.0.1:8088/api/v1/chart/data?form_data={form_data}&dashboard_id=2'

_, o, _ = ssh.exec_command(
    f'curl -s -X POST "{url}" -H "Authorization: Bearer {token}" -H "Content-Type: application/json"'
)
response = o.read().decode(errors='replace')
print('POST response (body):')
print(response[:1000])

# Also test GET endpoint for chart 5
print('\n--- GET chart 5 ---')
_, o2, _ = ssh.exec_command(
    'curl -s http://127.0.0.1:8088/api/v1/chart/5/data/ -H "Authorization: Bearer ' + token + '"'
)
resp2 = json.loads(o2.read().decode())
result = resp2.get("result", [{}])[0]
print(f'error: {result.get("error")}')
print(f'data count: {len(result.get("data", []))}')

ssh.close()
