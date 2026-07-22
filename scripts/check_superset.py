import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

cmds = [
    'docker ps --filter name=superset --format "{{.Names}} {{.Status}}"',
    'curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8088/api/v1/me/ 2>&1',
    'docker logs podft-superset --tail 5 2>&1',
    'curl -s -X POST http://127.0.0.1:8088/api/v1/security/login '
    '-H "Content-Type: application/json" '
    '-d \'{"username":"admin","password":"admin","provider":"db"}\' 2>&1',
]

for cmd in cmds:
    print(f'> {cmd[:80]}')
    stdin, stdout, stderr = ssh.exec_command(cmd)
    print(stdout.read().decode(errors='replace').strip()[:300])

ssh.close()
