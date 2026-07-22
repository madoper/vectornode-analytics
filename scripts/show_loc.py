import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=10)
stdin, stdout, stderr = ssh.exec_command("sed -n '149,168p' /etc/nginx/sites-enabled/vectornode.ru")
print(stdout.read().decode(errors='replace').strip())
ssh.close()
