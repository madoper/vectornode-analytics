import paramiko, json

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

# 1. Login via API (what SPA does)
stdin, stdout, stderr = ssh.exec_command(
    "curl -s -X POST https://vectornode.ru/superset/api/v1/security/login "
    "-H 'Content-Type: application/json' "
    "-d '{\"username\":\"admin\",\"password\":\"admin\",\"provider\":\"db\"}'"
)
login = json.loads(stdout.read().decode())
token = login.get('access_token', '')
print(f'1. API login: OK, token={token[:20]}...')

# 2. Access CSRF token (needed for some API calls)
stdin2, stdout2, stderr2 = ssh.exec_command(
    f"curl -s -H 'Authorization: Bearer {token}' "
    f"https://vectornode.ru/superset/api/v1/security/csrf_token/"
)
csrf = json.loads(stdout2.read().decode())
print(f'2. CSRF token: {csrf.get("result","")[:30]}...')

# 3. Access dashboard list via API
stdin3, stdout3, stderr3 = ssh.exec_command(
    f"curl -s -H 'Authorization: Bearer {token}' "
    f"https://vectornode.ru/superset/api/v1/dashboard/ | python3 -c "
    f"\"import sys,json;d=json.load(sys.stdin);print(f'3. Dashboards: {d.get(\\\"count\\\",0)}')\""
)
print(stdout3.read().decode(errors='replace').strip()[:200])

# 4. Access dataset list
stdin4, stdout4, stderr4 = ssh.exec_command(
    f"curl -s -H 'Authorization: Bearer {token}' "
    f"https://vectornode.ru/superset/api/v1/dataset/ | python3 -c "
    f"\"import sys,json;d=json.load(sys.stdin);print(f'4. Datasets: {d.get(\\\"count\\\",0)}')\""
)
print(stdout4.read().decode(errors='replace').strip()[:200])

# 5. Check if brand.path redirect works after auth
stdin5, stdout5, stderr5 = ssh.exec_command(
    f"curl -s -o /dev/null -w '%{{http_code}}' -H 'Authorization: Bearer {token}' "
    f"https://vectornode.ru/superset/welcome/"
)
print(f'5. Welcome page (auth): {stdout5.read().decode(errors="replace").strip()}')

# 6. Check Superset logs for errors
stdin6, stdout6, stderr6 = ssh.exec_command('docker logs podft-superset --tail 20 2>&1')
print('6. Logs:')
print(stdout6.read().decode(errors='replace').strip()[:1000])

ssh.close()
