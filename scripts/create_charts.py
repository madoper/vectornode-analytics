import paramiko, json

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

# Get token
stdin, stdout, stderr = ssh.exec_command(
    "curl -s -X POST http://127.0.0.1:8088/api/v1/security/login "
    "-H 'Content-Type: application/json' "
    "-d '{\"username\":\"admin\",\"password\":\"admin\",\"provider\":\"db\"}'"
)
token = json.loads(stdout.read().decode()).get('access_token', '')

# Get CSRF
stdin2, stdout2, stderr2 = ssh.exec_command(
    f"curl -s -c /tmp/sc2.txt -H 'Authorization: Bearer {token}' "
    f"http://127.0.0.1:8088/api/v1/security/csrf_token/"
)
csrf = json.loads(stdout2.read().decode()).get('result', '')
print(f'CSRF: {csrf[:20]}...')

# Create more charts
charts = [
    {"slice_name": "Interpretation breakdown", "viz_type": "pie", "datasource_id": 3, "datasource_type": "table",
     "params": json.dumps({"metrics": ["count"], "groupby": ["interpretation"]})},
    {"slice_name": "Hypothesis distribution", "viz_type": "bar_chart", "datasource_id": 3, "datasource_type": "table",
     "params": json.dumps({"metrics": ["count"], "groupby": ["hypothesis_code"]})},
    {"slice_name": "Anomalies table", "viz_type": "table", "datasource_id": 3, "datasource_type": "table",
     "params": json.dumps({"metrics": [], "groupby": [], "all_columns": ["company_id", "year", "hypothesis_code", "interpretation", "criticality"]})},
]

chart_ids = [1]
for ch in charts:
    payload = json.dumps(ch)
    stdin3, stdout3, stderr3 = ssh.exec_command(
        f"curl -s -X POST http://127.0.0.1:8088/api/v1/chart/ "
        f"-H 'Authorization: Bearer {token}' "
        f"-H 'Content-Type: application/json' "
        f"-H 'X-CSRFToken: {csrf}' "
        f"-b /tmp/sc2.txt "
        f"-d '{payload}'"
    )
    result = json.loads(stdout3.read().decode())
    cid = result.get('id')
    if cid:
        chart_ids.append(cid)
        name = ch["slice_name"]
        print(f'Chart created: {name} (id={cid})')
    else:
        print(f'Chart failed: {result}')

nl = '\n'
print(f'{nl}All chart IDs: {chart_ids}')

# Add charts to dashboard (dashboard id=2)
for cid in chart_ids:
    payload = '{"chart_id": ' + str(cid) + '}'
    stdin4, stdout4, stderr4 = ssh.exec_command(
        "curl -s -X POST http://127.0.0.1:8088/api/v1/dashboard/2/charts/ "
        "-H 'Authorization: Bearer " + token + "' "
        "-H 'Content-Type: application/json' "
        "-H 'X-CSRFToken: " + csrf + "' "
        "-b /tmp/sc2.txt "
        "-d '" + payload + "'"
    )
    result = stdout4.read().decode(errors='replace').strip()
    print(f'Added chart {cid} to dashboard: {result[:100]}')

ssh.close()
