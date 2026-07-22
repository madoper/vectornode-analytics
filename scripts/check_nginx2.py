import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

cmds = [
    'cat /etc/nginx/sites-enabled/vectornode.ru',
    'cat /opt/podft/infra/nginx/nginx-vps.conf',
]

for cmd in cmds:
    print(f'> {cmd}')
    stdin, stdout, stderr = ssh.exec_command(cmd)
    print(stdout.read().decode(errors='replace').strip())

ssh.close()
