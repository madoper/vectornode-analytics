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

# Correct payload format for chart data API
payload = json.dumps({
    "form_data": {
        "slice_id": 1,
        "viz_type": "bar_chart",
        "datasource": "3__table",
        "granularity_sqla": "year",
        "time_range": "No filter",
        "metrics": [{"expressionType": "SIMPLE", "aggregate": "COUNT", "column": {"column_name": "company_id"}, "label": "COUNT(company_id)"}],
        "groupby": ["criticality"],
        "row_limit": 10000
    },
    "queries": [{
        "groupby": ["criticality"],
        "metrics": [{"expressionType": "SIMPLE", "aggregate": "COUNT", "column": {"column_name": "company_id"}, "label": "COUNT(company_id)"}],
        "row_limit": 10000,
        "timeseries_limit": 0,
        "filters": [],
        "order_desc": True
    }],
    "result_type": "full"
})

result = run(
    f'curl -s -X POST http://127.0.0.1:8088/api/v1/chart/data '
    f'-H "Authorization: Bearer {token}" '
    f'-H "Content-Type: application/json" '
    f'-d \'{payload}\' 2>&1'
)
print(f'Chart data result: {result[:500]}')

# Also try the simpler format that the SPA uses
import urllib.parse
form_data_str = json.dumps({"slice_id": 1})
payload2 = json.dumps({
    "form_data": form_data_str,
    "queries": [{
        "groupby": ["criticality"],
        "metrics": [{"expressionType": "SIMPLE", "aggregate": "COUNT", "column": {"column_name": "company_id"}, "label": "COUNT(company_id)"}],
        "row_limit": 10000
    }]
})

result2 = run(
    f'curl -s -X POST http://127.0.0.1:8088/api/v1/chart/data '
    f'-H "Authorization: Bearer {token}" '
    f'-H "Content-Type: application/json" '
    f'-d \'{payload2}\' 2>&1'
)
print(f'\nWith string form_data: {result2[:500]}')

ssh.close()
