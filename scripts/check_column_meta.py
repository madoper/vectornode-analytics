import paramiko, json
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=10)

# Check column metadata for dataset 3
_, o, _ = ssh.exec_command(
    "docker exec podft-postgres psql -U podft -d superset -c "
    "\"SELECT id, column_name, type, is_dttm, python_date_format FROM table_columns WHERE table_id = 3 AND column_name = 'year'\""
)
print('Column metadata:')
print(o.read().decode(errors='replace'))

# Also check the dataset
_, o2, _ = ssh.exec_command(
    "docker exec podft-postgres psql -U podft -d superset -c "
    "\"SELECT id, table_name, main_dttm_col FROM tables WHERE id = 3\""
)
print('\nDataset:')
print(o2.read().decode(errors='replace'))

# Login and check via API
_, auth, _ = ssh.exec_command(
    'curl -s -X POST http://127.0.0.1:8088/api/v1/security/login -H "Content-Type: application/json" -d \'{"username":"admin","password":"admin","provider":"db"}\''
)
token = json.loads(auth.read().decode())["access_token"]

_, o3, _ = ssh.exec_command(
    'curl -s "http://127.0.0.1:8088/api/v1/dataset/3" -H "Authorization: Bearer ' + token + '"'
)
ds = json.loads(o3.read().decode())
cols = ds.get('result', {}).get('columns', [])
for col in cols:
    if col['column_name'] == 'year':
        print('\nyear column from API:')
        print(json.dumps(col, indent=2, ensure_ascii=False))
        break

ssh.close()
