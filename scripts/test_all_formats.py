import paramiko, json, base64, urllib.parse

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

# Try passing the EXPLICIT datasource in the POST body as JSON
form_data_obj = {
    "slice_id": 5,
    "datasource": "3__table",
    "viz_type": "bar_chart",
    "groupby": ["criticality"],
    "metrics": [{"expressionType": "SIMPLE", "aggregate": "COUNT", "column": {"column_name": "company_id"}, "label": "COUNT(company_id)"}],
    "row_limit": 1000
}

payload_body = json.dumps({
    "form_data": form_data_obj,
    "queries": [{
        "groupby": ["criticality"],
        "metrics": [{"expressionType": "SIMPLE", "aggregate": "COUNT", "column": {"column_name": "company_id"}, "label": "COUNT(company_id)"}],
        "row_limit": 1000
    }],
    "result_type": "full",
    "datasource": {"id": 3, "type": "table"}
})

# Try different payload formats
tests = [
    # 1: form_data as string with datasource, separate queries
    {
        "form_data": json.dumps(form_data_obj),
        "queries": [{"row_limit": 1000, "groupby": ["criticality"], "metrics": [{"expressionType": "SIMPLE", "aggregate": "COUNT", "column": {"column_name": "company_id"}, "label": "COUNT(company_id)"}]}],
        "datasource": {"id": 3, "type": "table"}
    },
    # 2: form_data as string, datasource in body
    {
        "form_data": json.dumps(form_data_obj),
        "datasource": {"id": 3, "type": "table"}
    },
    # 3: All in body as JSON object
    {
        "form_data": form_data_obj,
        "datasource": {"id": 3, "type": "table"}
    },
    # 4: As URL query param (SPA style) but with datasource in body
    form_data_obj,
]

for i, test in enumerate(tests):
    payload = json.dumps(test)
    result = run(
        f'curl -s -i -X POST http://127.0.0.1:8088/api/v1/chart/data '
        f'-H "Authorization: Bearer {token}" '
        f'-H "Content-Type: application/json" '
        f'-H "Accept: application/json" '
        f'-d \'{payload}\' 2>&1 | head -20'
    )
    if "200" in result.split('\n')[0]:
        print(f'Test {i+1}: SUCCESS!')
        body_start = result.find('\n\n')
        if body_start > 0:
            print(f'  Body: {result[body_start:body_start+200]}')
    else:
        status_line = result.split('\n')[0]
        body_start = result.find('\n\n')
        body = result[body_start:body_start+150] if body_start > 0 else result[:150]
        print(f'Test {i+1}: {status_line}  {body}')

ssh.close()
