import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

cmds = [
    'ls -la /opt/analytics/.git 2>&1',
    'cat /root/.ssh/authorized_keys | head -3 2>&1',
    'ls -la /root/.ssh/ 2>&1',
]

for cmd in cmds:
    stdin, stdout, stderr = ssh.exec_command(cmd)
    print(stdout.read().decode(errors='replace').strip()[:500])

ssh.close()
