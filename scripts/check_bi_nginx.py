import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

stdin, stdout, stderr = ssh.exec_command("grep -A20 'server_name bi.vectornode.ru' /etc/nginx/sites-enabled/vectornode.ru | head -25")
print(stdout.read().decode(errors='replace').strip())

ssh.close()
