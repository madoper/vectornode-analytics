import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

cmds = [
    'host admin.vectornode.ru 2>&1 || nslookup admin.vectornode.ru 2>&1 | head -5',
    'host bi.vectornode.ru 2>&1 || nslookup bi.vectornode.ru 2>&1 | head -5',
]

for cmd in cmds:
    stdin, stdout, stderr = ssh.exec_command(cmd)
    print(stdout.read().decode(errors='replace').strip()[:200])

ssh.close()
