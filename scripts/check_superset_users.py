import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

cmds = [
    'docker exec podft-superset superset fab list-users 2>&1',
    'ls /opt/podft/infra/superset/ 2>/dev/null || echo "no superset dir"',
    'find /opt/podft -name "superset*" -type f 2>/dev/null | head -10',
]

for cmd in cmds:
    print(f'> {cmd[:70]}')
    stdin, stdout, stderr = ssh.exec_command(cmd)
    print(stdout.read().decode(errors='replace').strip()[:600])

ssh.close()
