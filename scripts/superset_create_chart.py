import paramiko, json

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

def run(cmd):
    stdin, stdout, stderr = ssh.exec_command(cmd)
    return stdout.read().decode(errors='replace')

# Login via web endpoint to get Flask session cookie
login_resp = run(
    'curl -s -c /tmp/ss_cookies.txt -D - '
    '-X POST http://127.0.0.1:8088/login/ '
    '-d "username=admin&password=admin" '
    '-H "Content-Type: application/x-www-form-urlencoded" '
    '-H "Referer: http://127.0.0.1:8088/login/" 2>&1'
)
print('Login headers:', login_resp[:500])

# Get CSRF token  
csrf_resp = run(
    'curl -s -b /tmp/ss_cookies.txt -c /tmp/ss_cookies.txt '
    'http://127.0.0.1:8088/api/v1/security/csrf_token/ 2>&1'
)
csrf_data = json.loads(csrf_resp)
csrf = csrf_data.get('result', '')
print(f'CSRF: {csrf[:30]}...')

# Create dataset (table) for company_risk_summary
payload = json.dumps({
    "database": 1,
    "schema": "public_marts",
    "table_name": "company_risk_summary"
})
ds_resp = run(
    f'curl -s -b /tmp/ss_cookies.txt '
    f'-X POST http://127.0.0.1:8088/api/v1/explore/table/ '
    f'-H "Content-Type: application/json" '
    f'-H "X-CSRFToken: {csrf}" '
    f'-H "Referer: http://127.0.0.1:8088/superset/wizard/" '
    f'-d \'{payload}\' 2>&1'
)
print('Dataset creation:', ds_resp[:500])

ssh.close()
