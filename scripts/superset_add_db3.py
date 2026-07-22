import paramiko, json

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

def run(cmd):
    stdin, stdout, stderr = ssh.exec_command(cmd)
    return stdout.read().decode(errors='replace')

# Login with cookie jar
login_resp = run(
    'curl -s -c /tmp/superset_cookies.txt -X POST http://127.0.0.1:8088/api/v1/security/login '
    '-H "Content-Type: application/json" '
    '-d \'{"username":"admin","password":"admin","provider":"db"}\''
)
token = json.loads(login_resp).get('access_token', '')
print(f'Logged in, token: {token[:20]}...')

# Get CSRF token from session
csrf_resp = run(
    'curl -s -b /tmp/superset_cookies.txt http://127.0.0.1:8088/api/v1/security/csrf_token/ '
    f'-H "Authorization: Bearer {token}"'
)
csrf_data = json.loads(csrf_resp)
csrf = csrf_data.get('result', '')
print(f'CSRF token: {csrf[:30]}...')

# Add DB
db_payload = json.dumps({
    "database_name": "Analytics (dbt)",
    "sqlalchemy_uri": "postgresql://dbt_user:dbt_pass@podft-postgres:5432/analytics",
    "expose_in_sql_lab": True,
    "allow_run_async": True
})

db_resp = run(
    f'curl -s -X POST http://127.0.0.1:8088/api/v1/database/ '
    f'-H "Authorization: Bearer {token}" '
    f'-H "Content-Type: application/json" '
    f'-H "X-CSRFToken: {csrf}" '
    f'-b /tmp/superset_cookies.txt '
    f'-d \'{db_payload}\''
)
print('DB add response:', db_resp[:500])

# Check result
dbs = run(
    f'curl -s -b /tmp/superset_cookies.txt http://127.0.0.1:8088/api/v1/database/ '
    f'-H "Authorization: Bearer {token}"'
)
print('DBs:', dbs[:300])

ssh.close()
