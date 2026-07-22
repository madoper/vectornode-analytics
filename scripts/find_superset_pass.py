import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

# Try API login with admin/admin
cmd = "curl -s -X POST https://vectornode.ru/superset/api/v1/security/login -H 'Content-Type: application/json' -d '{\"username\":\"admin\",\"password\":\"admin\",\"provider\":\"db\"}'"
stdin, stdout, stderr = ssh.exec_command(cmd)
resp = stdout.read().decode(errors='replace').strip()
print('API login admin/admin:', resp[:100])

# Try common passwords
for pw in ['admin123', 'password', 'admin', 'podft', 'superset', 'changeme']:
    cmd2 = f"curl -s -X POST https://vectornode.ru/superset/api/v1/security/login -H 'Content-Type: application/json' -d '{{\"username\":\"admin\",\"password\":\"{pw}\",\"provider\":\"db\"}}'"
    stdin2, stdout2, stderr2 = ssh.exec_command(cmd2)
    r = stdout2.read().decode(errors='replace').strip()
    if 'access_token' in r:
        print(f'Found password: {pw}')
        break

# Check if there are other users
cmd3 = "docker exec podft-postgres psql -U podft -d superset -c 'SELECT id, username, email FROM ab_user'"
stdin3, stdout3, stderr3 = ssh.exec_command(cmd3)
print('\nSuperset users:', stdout3.read().decode(errors='replace').strip())

ssh.close()
