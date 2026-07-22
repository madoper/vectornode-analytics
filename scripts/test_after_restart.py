import paramiko, time, json

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

time.sleep(20)

# Check health
stdin, stdout, stderr = ssh.exec_command('curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8088/health')
health = stdout.read().decode(errors='replace').strip()
print(f'Health: {health}')

if health == '200':
    # Test chart data query
    login = ssh.exec_command(
        'curl -s -X POST http://127.0.0.1:8088/api/v1/security/login '
        '-H "Content-Type: application/json" '
        '-d \'{"username":"admin","password":"admin","provider":"db"}\''
    )
    token = json.loads(login[1].read().decode())["access_token"]
    
    # Query chart data - try without CSRF token
    payload = json.dumps({
        "form_data": json.dumps({"slice_id": 1}),
        "queries": [{
            "groupby": ["criticality"],
            "metrics": [{"expressionType": "SIMPLE", "aggregate": "COUNT", "column": {"column_name": "company_id"}, "label": "COUNT(company_id)"}]
        }],
        "slice_id": 1
    })
    
    query = ssh.exec_command(
        f'curl -s -X POST http://127.0.0.1:8088/api/v1/chart/data '
        f'-H "Authorization: Bearer {token}" '
        f'-H "Content-Type: application/json" '
        f'-d \'{payload}\' 2>&1'
    )
    result = query[1].read().decode(errors='replace').strip()
    print(f'Chart data result: {result[:300]}')

ssh.close()
