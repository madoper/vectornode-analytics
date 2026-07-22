import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

# First get access token
cmd = ('curl -s -X POST http://127.0.0.1:8088/api/v1/security/login '
       '-H "Content-Type: application/json" '
       '-d \'{"username":"admin","password":"admin","provider":"db"}\'')
stdin, stdout, stderr = ssh.exec_command(cmd)
import json
resp = json.loads(stdout.read().decode())
token = resp.get('access_token', '')
print(f'Token: {token[:30]}...')

# Check existing databases
cmd2 = f'curl -s http://127.0.0.1:8088/api/v1/database/ -H "Authorization: Bearer {token}"'
stdin2, stdout2, stderr2 = ssh.exec_command(cmd2)
dbs = json.loads(stdout2.read().decode())
print(f'Databases: {json.dumps(dbs, indent=2, ensure_ascii=False)[:1000]}')

ssh.close()
