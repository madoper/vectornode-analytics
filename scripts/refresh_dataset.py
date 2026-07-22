import paramiko, json

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

def run(cmd):
    stdin, stdout, stderr = ssh.exec_command(cmd)
    return stdout.read().decode(errors='replace').strip()

# Login
login = run(
    'curl -s -c /tmp/ss_dash.txt -X POST http://127.0.0.1:8088/api/v1/security/login '
    '-H "Content-Type: application/json" '
    '-d \'{"username":"admin","password":"admin","provider":"db"}\''
)
token = json.loads(login)["access_token"]

# Get CSRF
csrf_resp = run(
    f'curl -s -b /tmp/ss_dash.txt http://127.0.0.1:8088/api/v1/security/csrf_token/ '
    f'-H "Authorization: Bearer {token}"'
)
csrf = json.loads(csrf_resp)["result"]
print(f'CSRF: {csrf[:20]}...')

# Helper
def api(method, path, data=None):
    h = f'-H "Authorization: Bearer {token}" -H "Content-Type: application/json" -H "X-CSRFToken: {csrf}" -b /tmp/ss_dash.txt'
    d = f'-d \'{json.dumps(data)}\'' if data else ''
    cmd = f'curl -s -X {method} http://127.0.0.1:8088/api/v1/{path} {h} {d}'
    return run(cmd)

# Try to refresh dataset columns
# First check current dataset status
ds_info = api("GET", "dataset/3")
print('Dataset cols:', len(json.loads(ds_info).get("result", {}).get("columns", [])))

# Refresh dataset by executing a sync
# The endpoint is PUT /api/v1/dataset/{pk} with action columns
refresh = api("PUT", "dataset/3", {
    "table_name": "v_company_dashboard",
    "database": 1,
    "schema": "analytics",
})
print('Refresh:', refresh[:200])

# Try getting the table columns via the api
table = api("GET", "dataset/3/columns")
print('Columns:', table[:300])

ssh.close()
