import paramiko, json

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

def run(cmd):
    stdin, stdout, stderr = ssh.exec_command(cmd)
    return stdout.read().decode(errors='replace').strip()

# Login
login = run(
    'curl -s -c /tmp/ss_data.txt -X POST http://127.0.0.1:8088/api/v1/security/login '
    '-H "Content-Type: application/json" '
    '-d \'{"username":"admin","password":"admin","provider":"db"}\''
)
token = json.loads(login)["access_token"]

# Get CSRF
csrf_resp = run(
    f'curl -s -b /tmp/ss_data.txt http://127.0.0.1:8088/api/v1/security/csrf_token/ '
    f'-H "Authorization: Bearer {token}"'
)
csrf = json.loads(csrf_resp)["result"]

# Try to query chart data directly
# First check what params chart 1 has
chart_info = run(
    f'curl -s -H "Authorization: Bearer {token}" http://127.0.0.1:8088/api/v1/chart/1'
)
print("Chart 1 info:")
print(chart_info[:500])

# Try querying the chart data endpoint
form_data = json.dumps({"slice_id": 1})
data_payload = json.dumps({
    "form_data": form_data,
    "queries": [{
        "groupby": ["criticality"],
        "metrics": [{"expressionType": "SIMPLE", "aggregate": "COUNT", "column": {"column_name": "company_id"}, "label": "COUNT(company_id)"}],
        "row_limit": 10000,
        "timeseries_limit": 0,
        "filters": [],
        "order_desc": True
    }],
    "result_type": "full",
    "slice_id": 1
})

query_cmd = (
    f'curl -s -X POST http://127.0.0.1:8088/api/v1/chart/data '
    f'-H "Authorization: Bearer {token}" '
    f'-H "Content-Type: application/json" '
    f'-H "X-CSRFToken: {csrf}" '
    f'-b /tmp/ss_data.txt '
    f'-d \'{data_payload}\' 2>&1'
)
result = run(query_cmd)
print(f'\nChart data result: {result[:500]}')

ssh.close()
