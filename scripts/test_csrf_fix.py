import paramiko, json, time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

def run(cmd):
    stdin, stdout, stderr = ssh.exec_command(cmd)
    return stdout.read().decode(errors='replace').strip()

# Login to get JWT
login = run(
    'curl -s -c /tmp/ss_cs.txt -X POST http://127.0.0.1:8088/api/v1/security/login '
    '-H "Content-Type: application/json" '
    '-d \'{"username":"admin","password":"admin","provider":"db"}\''
)
token = json.loads(login)["access_token"]

# Get CSRF token
csrf_resp = run(
    f'curl -s -b /tmp/ss_cs.txt http://127.0.0.1:8088/api/v1/security/csrf_token/ '
    f'-H "Authorization: Bearer {token}"'
)
csrf = json.loads(csrf_resp).get("result", "")
print(f"CSRF token: {csrf[:20]}...")

# Now query chart data WITH CSRF token and session cookie
payload = json.dumps({
    "form_data": json.dumps({"slice_id": 1}),
    "queries": [{
        "groupby": ["criticality"],
        "metrics": [{"expressionType": "SIMPLE", "aggregate": "COUNT", "column": {"column_name": "company_id"}, "label": "COUNT(company_id)"}]
    }],
    "slice_id": 1
})

query_cmd = (
    f'curl -s -X POST http://127.0.0.1:8088/api/v1/chart/data '
    f'-H "Authorization: Bearer {token}" '
    f'-H "Content-Type: application/json" '
    f'-H "X-CSRFToken: {csrf}" '
    f'-b /tmp/ss_cs.txt '
    f'-d \'{payload}\' 2>&1'
)
result = run(query_cmd)
print(f'Chart data: {result[:400]}')

# If the above failed, try with JWT but no CSRF (in case exempt works)
result2 = run(
    f'curl -s -X POST http://127.0.0.1:8088/api/v1/chart/data '
    f'-H "Authorization: Bearer {token}" '
    f'-H "Content-Type: application/json" '
    f'-d \'{payload}\' 2>&1'
)
print(f'\nWithout CSRF: {result2[:400]}')

ssh.close()
