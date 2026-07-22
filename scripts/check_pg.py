import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

cmds = [
    'docker ps --format "{{.Names}} {{.Status}}"',
    'docker exec podft-postgres psql -U postgres -c "\\du" 2>/dev/null || docker exec $(docker ps --format "{{.Names}}" | grep postgres) psql -U postgres -c "\\du" 2>/dev/null',
]

for cmd in cmds:
    print('=== ' + cmd + ' ===')
    stdin, stdout, stderr = ssh.exec_command(cmd)
    print(stdout.read().decode().strip())
    err = stderr.read().decode().strip()
    if err:
        print('STDERR:', err)

ssh.close()
