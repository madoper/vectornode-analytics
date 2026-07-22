import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

cmds = [
    'dig admin.vectornode.ru +short 2>&1 || echo "dig not available"',
    'dig bi.vectornode.ru +short 2>&1 || echo "dig not available"',
    'getent hosts admin.vectornode.ru 2>&1',
    'getent hosts bi.vectornode.ru 2>&1',
]

for cmd in cmds:
    stdin, stdout, stderr = ssh.exec_command(cmd)
    print(f'> {cmd[:40]}')
    print(stdout.read().decode(errors='replace').strip()[:200])

ssh.close()
