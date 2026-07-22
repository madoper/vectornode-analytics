import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

stdin, stdout, stderr = ssh.exec_command('cat /root/.ssh/authorized_keys')
print(stdout.read().decode(errors='replace').strip()[:500])

ssh.close()
