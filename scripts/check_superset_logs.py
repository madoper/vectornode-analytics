import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', port=22, username='root', password='8884&JKL%f75', timeout=10)

# Get full error logs
_, o, _ = ssh.exec_command('docker logs podft-superset --since 2m 2>&1 | tail -40')
print('Full logs:')
print(o.read().decode(errors='replace'))

ssh.close()
