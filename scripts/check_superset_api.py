import paramiko, json

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

# Test Superset API through bi.vectornode.ru
stdin, stdout, stderr = ssh.exec_command(
    "curl -s -X POST http://127.0.0.1:8088/api/v1/security/login "
    "-H 'Content-Type: application/json' "
    "-d '{\"username\":\"admin\",\"password\":\"admin\",\"provider\":\"db\"}'"
)
resp = json.loads(stdout.read().decode())
token = resp.get('access_token', '')
print(f'Token: {token[:20]}...')

# Test database list
stdin2, stdout2, stderr2 = ssh.exec_command(
    f"curl -s -H 'Authorization: Bearer {token}' "
    f"http://127.0.0.1:8088/api/v1/database/"
)
dbs = json.loads(stdout2.read().decode())
print(f'\nDatabases: {dbs.get("count", 0)}')
for db in dbs.get('result', []):
    print(f'  - {db.get("database_name")} (id={db.get("id")})')

# Test dataset list
stdin3, stdout3, stderr3 = ssh.exec_command(
    f"curl -s -H 'Authorization: Bearer {token}' "
    f"http://127.0.0.1:8088/api/v1/dataset/"
)
ds = json.loads(stdout3.read().decode())
print(f'\nDatasets: {ds.get("count", 0)}')

ssh.close()
