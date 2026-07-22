import paramiko, json
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', port=22, username='root', password='8884&JKL%f75', timeout=10)

# Login
_, auth, _ = ssh.exec_command(
    'curl -s -X POST http://127.0.0.1:8088/api/v1/security/login -H "Content-Type: application/json" -d \'{"username":"admin","password":"admin","provider":"db"}\''
)
token = json.loads(auth.read().decode(errors='replace'))["access_token"]
print('Login OK')

# Step 1: Get dataset info
_, ds, _ = ssh.exec_command(
    'curl -s http://127.0.0.1:8088/api/v1/dataset/3 -H "Authorization: Bearer ' + token + '"'
)
ds_info = json.loads(ds.read().decode(errors='replace'))
result = ds_info.get('result', {})
print(f'Dataset: {result.get("table_name")} (id={result.get("id")})')
print(f'  schema: {result.get("schema")}')
print(f'  database: {result.get("database", {}).get("database_name")}')
print(f'  kind: {result.get("kind")}')
print(f'  columns: {len(result.get("columns", []))}')

# Step 2: Refresh dataset (sync columns from DB)
_, refresh, _ = ssh.exec_command(
    'curl -s -X PUT "http://127.0.0.1:8088/api/v1/dataset/3/refresh" '
    '-H "Content-Type: application/json" '
    '-H "Authorization: Bearer ' + token + '" '
    '-d \'{"datasource_type": "table"}\''
)
ref_result = refresh.read().decode(errors='replace')
print(f'\nRefresh: {ref_result[:200]}')

# Step 3: Verify columns after refresh
_, ds2, _ = ssh.exec_command(
    'curl -s http://127.0.0.1:8088/api/v1/dataset/3 -H "Authorization: Bearer ' + token + '"'
)
ds2_info = json.loads(ds2.read().decode(errors='replace'))
cols = ds2_info.get('result', {}).get('columns', [])
print(f'\nAfter refresh: {len(cols)} columns')
for c in cols[:5]:
    print(f'  {c["column_name"]}: {c["type"]} (is_dttm={c["is_dttm"]})')

# Step 4: Test the chart data API
fd = '{"slice_id":1}'
import urllib.parse
_, chart, _ = ssh.exec_command(
    'curl -s -w "\nHTTP_%{http_code}" -X POST "http://127.0.0.1:8088/api/v1/chart/data?form_data=' + urllib.parse.quote(fd) + '" '
    '-H "Content-Type: application/json" '
    '-H "Authorization: Bearer ' + token + '"'
)
out = chart.read().decode(errors='replace')
if 'HTTP_200' in out:
    print('\nChart API: OK')
elif 'HTTP_302' in out:
    print('\nChart API: 302 (middleware redirect - OK)')
else:
    print(f'\nChart API: {out[:200]}')

ssh.close()
