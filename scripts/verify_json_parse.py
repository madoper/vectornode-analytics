import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

# Verify injection works in HTTP response
stdin, stdout, stderr = ssh.exec_command(
    "curl -s https://vectornode.ru/superset/login/ 2>&1 | grep -c '_p.apply'"
)
print(f'Injection in HTTP: {stdout.read().decode(errors="replace").strip()}')

# Also test that API calls work
token_cmd = "curl -s -X POST https://vectornode.ru/superset/api/v1/security/login -H 'Content-Type: application/json' -d '{\"username\":\"admin\",\"password\":\"admin\",\"provider\":\"db\"}'"
stdin2, stdout2, stderr2 = ssh.exec_command(token_cmd)
import json
resp = json.loads(stdout2.read().decode())
token = resp.get('access_token', '')

# Test database API
stdin3, stdout3, stderr3 = ssh.exec_command(
    f"curl -s -H 'Authorization: Bearer {token}' "
    f"https://vectornode.ru/superset/api/v1/database/ | python3 -c "
    f"\"import sys,json;d=json.load(sys.stdin);print('Databases:',d.get('count',0))\""
)
print(stdout3.read().decode(errors='replace').strip())

ssh.close()
