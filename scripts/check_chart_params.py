import paramiko, json

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

def run(cmd):
    stdin, stdout, stderr = ssh.exec_command(cmd)
    return stdout.read().decode(errors='replace').strip()

# Check stored chart params
stdin, stdout, stderr = ssh.exec_command(
    "docker exec podft-postgres psql -U podft -d superset -c \"SELECT id, slice_name, params::text FROM slices WHERE id IN (1,2,3,4)\" 2>&1"
)
print(stdout.read().decode(errors='replace').strip()[:1000])

# Login 
login = run(
    'curl -s -X POST http://127.0.0.1:8088/api/v1/security/login '
    '-H "Content-Type: application/json" '
    '-d \'{"username":"admin","password":"admin","provider":"db"}\''
)
token = json.loads(login)["access_token"]

# Try the exact format the SPA uses - just slice_id in form_data
# The API should load chart params from DB
payload = json.dumps({
    "form_data": json.dumps({"slice_id": 1}),
    "queries": [{"row_limit": 10000}],
    "result_type": "full"
})

result = run(
    f'curl -s -i -X POST http://127.0.0.1:8088/api/v1/chart/data '
    f'-H "Authorization: Bearer {token}" '
    f'-H "Content-Type: application/json" '
    f'-H "Accept: application/json" '
    f'-d \'{payload}\' 2>&1 | head -30'
)
print(f'\nResult: {result[:600]}')

ssh.close()
