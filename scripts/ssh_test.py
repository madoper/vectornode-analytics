import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
try:
    ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)
    stdin, stdout, stderr = ssh.exec_command('hostname')
    print(stdout.read().decode().strip())
    ssh.close()
    print('SUCCESS')
except Exception as e:
    print('FAILED: ' + str(e))
