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

# Correct payload with datasource
form_data = json.dumps({
    "slice_id": 1,
    "datasource": "3__table",
    "viz_type": "bar_chart",
    "granularity_sqla": "year",
    "time_range": "No filter",
    "metrics": [{"expressionType": "SIMPLE", "aggregate": "COUNT", "column": {"column_name": "company_id"}, "label": "COUNT(company_id)"}],
    "groupby": ["criticality"],
    "row_limit": 10000,
    "order_desc": True
})

payload = json.dumps({
    "form_data": form_data,
    "queries": [{
        "groupby": ["criticality"],
        "metrics": [{"expressionType": "SIMPLE", "aggregate": "COUNT", "column": {"column_name": "company_id"}, "label": "COUNT(company_id)"}],
        "row_limit": 10000
    }],
    "result_type": "full"
})

result = run(
    f'curl -s -X POST http://127.0.0.1:8088/api/v1/chart/data '
    f'-H "Authorization: Bearer {token}" '
    f'-H "Content-Type: application/json" '
    f'-H "Accept: application/json" '
    f'-d \'{payload}\' 2>&1'
)
print(f'Result: {result[:600]}')

ssh.close()
