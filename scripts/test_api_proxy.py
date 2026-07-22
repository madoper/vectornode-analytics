import paramiko, json

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

# Login to get token
stdin, stdout, stderr = ssh.exec_command(
    "curl -s -X POST https://vectornode.ru/superset/api/v1/security/login "
    "-H 'Content-Type: application/json' "
    "-d '{\"username\":\"admin\",\"password\":\"admin\",\"provider\":\"db\"}'"
)
token = json.loads(stdout.read().decode()).get('access_token', '')

# Test /api/v1/database/ (without /superset/ prefix) with auth
stdin2, stdout2, stderr2 = ssh.exec_command(
    f"curl -s -H 'Authorization: Bearer {token}' "
    f"https://vectornode.ru/api/v1/database/ | python3 -c "
    f"\"import sys,json;d=json.load(sys.stdin);print('Databases:',d.get('count',0))\""
)
print(stdout2.read().decode(errors='replace').strip())

# Test /api/v1/dashboard/ with auth
stdin3, stdout3, stderr3 = ssh.exec_command(
    f"curl -s -H 'Authorization: Bearer {token}' "
    f"https://vectornode.ru/api/v1/dashboard/ | python3 -c "
    f"\"import sys,json;d=json.load(sys.stdin);print('Dashboards:',d.get('count',0))\""
)
print(stdout3.read().decode(errors='replace').strip())

# Test /api/health (should still go to gateway)
stdin4, stdout4, stderr4 = ssh.exec_command(
    "curl -s -o /dev/null -w '%{http_code}' https://vectornode.ru/api/health"
)
print(f'/api/health (gateway): {stdout4.read().decode(errors="replace").strip()}')

# Test /api/ with a gateway route
stdin5, stdout5, stderr5 = ssh.exec_command(
    "curl -s -o /dev/null -w '%{http_code}' https://vectornode.ru/api/"
)
print(f'/api/ (gateway): {stdout5.read().decode(errors="replace").strip()}')

ssh.close()
