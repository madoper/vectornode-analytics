import paramiko, json, urllib.parse, time
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=10)

time.sleep(5)

# Login
_, auth, _ = ssh.exec_command(
    'curl -s -X POST http://127.0.0.1:8088/api/v1/security/login -H "Content-Type: application/json" -d \'{"username":"admin","password":"admin","provider":"db"}\''
)
token = json.loads(auth.read().decode(errors='replace'))["access_token"]
print('Login OK')

# Test 1: chart POST with form_data ONLY in query string (no body)
fd = urllib.parse.quote('{"slice_id":5}')
_, o, _ = ssh.exec_command(
    'curl -s -w "\nHTTP_%{http_code}" -X POST "http://127.0.0.1:8088/api/v1/chart/data?form_data=' + fd + '" '
    '-H "Authorization: Bearer ' + token + '"'
)
print('\nTest 1 - Chart POST (query string only, no body):')
print(o.read().decode(errors='replace')[:500])

# Test 2: native filter POST
_, o2, _ = ssh.exec_command(
    'curl -s -w "\nHTTP_%{http_code}" -X POST http://127.0.0.1:8088/api/v1/chart/data '
    '-H "Content-Type: application/json" '
    '-H "Authorization: Bearer ' + token + '" '
    '-d \'{"datasource":{"id":3,"type":"table"},"queries":[{"columns":["year"],"row_limit":5}]}\''
)
print('\n\nTest 2 - Native filter POST:')
print(o2.read().decode(errors='replace')[:400])

# Test 3: chart POST with JSON body (has filter context)
_, o3, _ = ssh.exec_command(
    'curl -s -w "\nHTTP_%{http_code}" -X POST http://127.0.0.1:8088/api/v1/chart/data '
    '-H "Content-Type: application/json" '
    '-H "Authorization: Bearer ' + token + '" '
    '-d \'{"datasource":{"id":3,"type":"table"},"queries":[{"groupby":["criticality"],"metrics":[{"aggregate":"COUNT","column":{"column_name":"company_id"},"expressionType":"SIMPLE"}],"filters":[{"col":"year","op":"==","val":2024}]}]}\''
)
print('\n\nTest 3 - Chart POST with year filter:')
print(o3.read().decode(errors='replace')[:500])

ssh.close()
