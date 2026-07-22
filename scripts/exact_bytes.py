import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

stdin, stdout, stderr = ssh.exec_command(
    "grep -B1 -A12 'location /login/' /etc/nginx/sites-enabled/vectornode.ru"
)
print(repr(stdout.read().decode('utf-8', errors='replace')))

ssh.close()
