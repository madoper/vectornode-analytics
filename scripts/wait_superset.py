import paramiko, time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

time.sleep(30)

# Check health
stdin, stdout, stderr = ssh.exec_command('curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8088/health')
health = stdout.read().decode(errors='replace').strip()
print(f'Health: {health}')

# Check login page
stdin2, stdout2, stderr2 = ssh.exec_command('curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8088/login/')
login_page = stdout2.read().decode(errors='replace').strip()
print(f'Login page: {login_page}')

# Check docker status
stdin3, stdout3, stderr3 = ssh.exec_command('docker ps --filter name=superset --format "{{.Names}} {{.Status}}"')
print(f'Status: {stdout3.read().decode(errors="replace").strip()}')

ssh.close()
