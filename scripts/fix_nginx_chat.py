import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=10, look_for_keys=False, allow_agent=False)

sftp = ssh.open_sftp()
sftp.put(r'C:\Users\madop\AppData\Local\Temp\opencode\nginx_fix.py', '/tmp/nginx_fix.py')
sftp.close()

stdin, stdout, stderr = ssh.exec_command('python3 /tmp/nginx_fix.py')
print('OUT:', stdout.read().decode())
print('ERR:', stderr.read().decode())

stdin, stdout, stderr = ssh.exec_command('nginx -t 2>&1')
print('nginx -t:', stdout.read().decode(), stderr.read().decode())

stdin, stdout, stderr = ssh.exec_command('systemctl reload nginx')
print('reload:', stdout.read().decode(), stderr.read().decode())

ssh.close()
