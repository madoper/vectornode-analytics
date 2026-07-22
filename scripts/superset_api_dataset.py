import paramiko, json

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

def run(cmd):
    stdin, stdout, stderr = ssh.exec_command(cmd)
    return stdout.read().decode(errors='replace')

# Use API login with proper Accept header
login_resp = run(
    'curl -s -X POST http://127.0.0.1:8088/api/v1/security/login '
    '-H "Content-Type: application/json" '
    '-H "Accept: application/json" '
    '-d \'{"username":"admin","password":"admin","provider":"db"}\''
)
token = json.loads(login_resp).get('access_token', '')
print(f'Token OK: {token[:20]}...')

# Create dataset via API (should not require CSRF with JWT)
dataset_payload = json.dumps({
    "database": 1,
    "catalog": None,
    "schema": "public_marts",
    "table_name": "company_risk_summary"
})
ds_resp = run(
    f'curl -s -X POST http://127.0.0.1:8088/api/v1/dataset/ '
    f'-H "Authorization: Bearer {token}" '
    f'-H "Content-Type: application/json" '
    f'-H "Accept: application/json" '
    f'-d \'{dataset_payload}\''
)
print(f'Dataset response: {ds_resp[:600]}')

ssh.close()
