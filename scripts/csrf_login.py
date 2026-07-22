import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

# 1. Login via API to get JWT
token_resp = "curl -s -X POST https://vectornode.ru/superset/api/v1/security/login -H 'Content-Type: application/json' -d '{\"username\":\"admin\",\"password\":\"admin\",\"provider\":\"db\"}'"
stdin, stdout, stderr = ssh.exec_command(token_resp)
import json
resp = json.loads(stdout.read().decode())
jwt = resp.get('access_token', '')
print(f'JWT: {jwt[:30]}...')

# 2. Get CSRF token using JWT
csrf_resp = f"curl -s -H 'Authorization: Bearer {jwt}' https://vectornode.ru/superset/api/v1/security/csrf_token/"
stdin2, stdout2, stderr2 = ssh.exec_command(csrf_resp)
csrf_data = json.loads(stdout2.read().decode())
csrf_token = csrf_data.get('result', '')
print(f'CSRF token: {csrf_token[:30]}...')

# 3. Now use the session cookie + CSRF to POST to /login/
login_form = (
    f"curl -s -D - -o /dev/null "
    f"-b /tmp/ss_cookies.txt -c /tmp/ss_cookies.txt "
    f"-X POST https://vectornode.ru/superset/login/ "
    f"-d 'username=admin&password=admin&csrf_token={csrf_token}' "
    f"-H 'Content-Type: application/x-www-form-urlencoded' "
    f"-H 'Referer: https://vectornode.ru/superset/login/' 2>&1 | head -15"
)
stdin3, stdout3, stderr3 = ssh.exec_command(login_form)
print('\nWeb login with CSRF:')
print(stdout3.read().decode(errors='replace').strip())

# Also try through /login/ (our fallback location)
stdin4, stdout4, stderr4 = ssh.exec_command(
    f"curl -s -D - -o /dev/null "
    f"-X POST https://vectornode.ru/login/ "
    f"-d 'username=admin&password=admin&csrf_token={csrf_token}' "
    f"-H 'Content-Type: application/x-www-form-urlencoded' "
    f"-H 'Referer: https://vectornode.ru/login/' 2>&1 | head -15"
)
print('\n/login/ POST with CSRF:')
print(stdout4.read().decode(errors='replace').strip())

ssh.close()
