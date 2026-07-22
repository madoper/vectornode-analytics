import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

# Read the vps compose
stdin, stdout, stderr = ssh.exec_command('cat /opt/podft/docker-compose.vps.yml')
compose = stdout.read().decode('utf-8', errors='replace')
print(compose)
ssh.close()
