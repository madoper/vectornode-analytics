import paramiko, json

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

def run(cmd):
    stdin, stdout, stderr = ssh.exec_command(cmd)
    return stdout.read().decode(errors='replace').strip()

# Login
login = run(
    'curl -s -X POST http://127.0.0.1:8088/api/v1/security/login '
    '-H "Content-Type: application/json" '
    '-d \'{"username":"admin","password":"admin","provider":"db"}\''
)
token = json.loads(login)["access_token"]
print(f'Token OK')

# Test chart data (no CSRF needed if disabled)
payload = json.dumps({
    "form_data": json.dumps({"slice_id": 1}),
    "queries": [{
        "groupby": ["criticality"],
        "metrics": [{"expressionType": "SIMPLE", "aggregate": "COUNT", "column": {"column_name": "company_id"}, "label": "COUNT(company_id)"}]
    }],
    "slice_id": 1
})

result = run(
    f'curl -s -X POST http://127.0.0.1:8088/api/v1/chart/data '
    f'-H "Authorization: Bearer {token}" '
    f'-H "Content-Type: application/json" '
    f'-d \'{payload}\' 2>&1'
)
print(f'Chart data: {result[:500]}')

# Check chart data from bi.vectornode.ru
result2 = run(
    f'curl -s -X POST https://bi.vectornode.ru/api/v1/chart/data '
    f'-H "Authorization: Bearer {token}" '
    f'-H "Content-Type: application/json" '
    f'-d \'{payload}\' 2>&1'
)
print(f'\nVia bi.vectornode.ru: {result2[:500]}')

ssh.close()
