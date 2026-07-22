import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

cmd = 'docker exec podft-postgres psql -U postgres -c "\\du"'
stdin, stdout, stderr = ssh.exec_command(cmd)
print('STDOUT:')
print(stdout.read().decode().strip())
print('STDERR:')
print(stderr.read().decode().strip())

ssh.close()
