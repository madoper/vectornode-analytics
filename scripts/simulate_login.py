import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

# Simulate full login flow
# 1. Get CSRF token via API
stdin, stdout, stderr = ssh.exec_command(
    "curl -s -X POST https://vectornode.ru/superset/api/v1/security/login "
    "-H 'Content-Type: application/json' "
    "-d '{\"username\":\"admin\",\"password\":\"admin\",\"provider\":\"db\"}'"
)
import json
login_resp = json.loads(stdout.read().decode())
token = login_resp.get('access_token', '')
print(f'Login OK, token: {token[:20]}...')

# 2. Access user_info via /superset/user_info/
stdin2, stdout2, stderr2 = ssh.exec_command(
    f"curl -s -H 'Authorization: Bearer {token}' https://vectornode.ru/superset/user_info/"
)
print(f'user_info via /superset/: {stdout2.read().decode(errors="replace").strip()[:200]}')

# 3. Access user_info via /user_info/ (SPA path)
stdin3, stdout3, stderr3 = ssh.exec_command(
    f"curl -s -H 'Authorization: Bearer {token}' https://vectornode.ru/user_info/"
)
print(f'user_info via /: {stdout3.read().decode(errors="replace").strip()[:200]}')

# 4. Check if Superset API v1 works
stdin4, stdout4, stderr4 = ssh.exec_command(
    f"curl -s -H 'Authorization: Bearer {token}' https://vectornode.ru/superset/api/v1/dashboard/ | python3 -c 'import sys,json;d=json.load(sys.stdin);print(f\"Dashboards: {d.get(chr(99)+chr(111)+chr(117)+chr(110)+chr(116),0)}\")'"
)
print(stdout4.read().decode(errors='replace').strip()[:200])

ssh.close()
