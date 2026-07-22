import paramiko, json, time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

# Get JWT
stdin, stdout, stderr = ssh.exec_command(
    "curl -s -X POST http://127.0.0.1:8088/api/v1/security/login "
    "-H 'Content-Type: application/json' "
    "-d '{\"username\":\"admin\",\"password\":\"admin\",\"provider\":\"db\"}'"
)
token = json.loads(stdout.read().decode()).get('access_token', '')

# Get CSRF token
stdin2, stdout2, stderr2 = ssh.exec_command(
    f"curl -s -c /tmp/ss_cookies.txt "
    f"-H 'Authorization: Bearer {token}' "
    f"http://127.0.0.1:8088/api/v1/security/csrf_token/"
)
csrf_data = json.loads(stdout2.read().decode())
csrf = csrf_data.get('result', '')
print(f'CSRF: {csrf[:30]}...')

# Create a chart (slice)
chart_payload = json.dumps({
    "datasource_id": 3,
    "datasource_type": "table",
    "slice_name": "Criticality distribution",
    "viz_type": "bar_chart",
    "params": json.dumps({
        "metrics": ["count"],
        "groupby": ["criticality"],
        "time_range": "No filter"
    })
})

cmd3 = (
    f"curl -s -X POST http://127.0.0.1:8088/api/v1/chart/ "
    f"-H 'Authorization: Bearer {token}' "
    f"-H 'Content-Type: application/json' "
    f"-H 'X-CSRFToken: {csrf}' "
    f"-b /tmp/ss_cookies.txt "
    f"-d '{chart_payload}'"
)
stdin3, stdout3, stderr3 = ssh.exec_command(cmd3)
result = json.loads(stdout3.read().decode())
print(f'Chart result: {json.dumps(result, indent=2)[:500]}')

# If CSRF issue, try using only JWT
stdin4, stdout4, stderr4 = ssh.exec_command(
    f"curl -s -v -X POST http://127.0.0.1:8088/api/v1/chart/ "
    f"-H 'Authorization: Bearer {token}' "
    f"-H 'Content-Type: application/json' "
    f"-d '{chart_payload}' 2>&1 | head -30"
)
print(f'\nDirect API: {stdout4.read().decode(errors="replace").strip()[:500]}')

ssh.close()
