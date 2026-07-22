import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

cmd = 'echo "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAILcnttWnZQagP/JdSh5rJfqQS9AhrcpMwLMSVIjnaDoV madop@MADOPER-ASUS" >> /root/.ssh/authorized_keys && echo OK'
stdin, stdout, stderr = ssh.exec_command(cmd)
print(stdout.read().decode(errors='replace').strip())

ssh.close()
