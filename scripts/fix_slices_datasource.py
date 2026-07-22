import paramiko, json, base64

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

def run(cmd):
    stdin, stdout, stderr = ssh.exec_command(cmd)
    return stdout.read().decode(errors='replace').strip()

# Fix all slices to have datasource_id and datasource_type
sql = """
UPDATE slices 
SET datasource_id = 3, 
    datasource_type = 'table',
    datasource_name = 'v_company_dashboard'
WHERE table_id = 3 OR id IN (1,2,3,4,5)
"""
stdin, stdout, stderr = ssh.exec_command(
    f'docker exec -i podft-postgres psql -U podft -d superset -c "{sql}" 2>&1'
)
print('Update:', stdout.read().decode(errors='replace').strip())

# Verify
stdin2, stdout2, stderr2 = ssh.exec_command(
    "docker exec podft-postgres psql -U podft -d superset -c \"SELECT id, slice_name, datasource_id, datasource_type FROM slices ORDER BY id\" 2>&1"
)
print('\nSlices:')
print(stdout2.read().decode(errors='replace').strip()[:800])

# Now test chart data API
# Login
login_resp = run(
    'curl -s -X POST http://127.0.0.1:8088/api/v1/security/login '
    '-H "Content-Type: application/json" '
    '-d \'{"username":"admin","password":"admin","provider":"db"}\''
)
token = json.loads(login_resp)["access_token"]

# Test with just slice_id in form_data (SPA format)
form_data = json.dumps({"slice_id": 1})
payload = json.dumps({
    "form_data": form_data,
    "queries": [{"row_limit": 1000}]
})

result = run(
    f'curl -s -i -X POST http://127.0.0.1:8088/api/v1/chart/data '
    f'-H "Authorization: Bearer {token}" '
    f'-H "Content-Type: application/json" '
    f'-H "Accept: application/json" '
    f'-d \'{payload}\' 2>&1 | head -30'
)
print(f'\nChart data test: {result[:500]}')

# Also try URL param as SPA does
form_data_url = json.dumps({"slice_id": 1})
result2 = run(
    f'curl -s -i -X POST "http://127.0.0.1:8088/api/v1/chart/data?form_data={form_data_url}" '
    f'-H "Authorization: Bearer {token}" '
    f'-H "Content-Type: application/json" '
    f'-H "Accept: application/json" '
    f'-d \'{{}}\' 2>&1 | head -30'
)
print(f'\nURL param test: {result2[:500]}')

ssh.close()
