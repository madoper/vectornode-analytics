import paramiko, time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

# Restart Superset
stdin, stdout, stderr = ssh.exec_command('docker restart podft-superset 2>&1')
print('Restart:', stdout.read().decode(errors='replace').strip())

time.sleep(15)

# Check health
stdin2, stdout2, stderr2 = ssh.exec_command(
    'docker ps --filter name=superset --format "{{.Names}} {{.Status}}"'
)
print('Status:', stdout2.read().decode(errors='replace').strip())

# Test login page
stdin3, stdout3, stderr3 = ssh.exec_command(
    'curl -s -o /dev/null -w "%{http_code}" https://vectornode.ru/superset/login/'
)
print('Login page:', stdout3.read().decode(errors='replace').strip())

# Check bootstrap data for user_login_url
stdin4, stdout4, stderr4 = ssh.exec_command(
    "curl -s https://vectornode.ru/superset/login/ 2>&1 | grep -oP 'user_login_url[^,}]*'"
)
print('\nuser_login_url:', stdout4.read().decode(errors='replace').strip())

# Check for application_root
stdin5, stdout5, stderr5 = ssh.exec_command(
    "curl -s https://vectornode.ru/superset/login/ 2>&1 | grep -oP 'application_root[^,}]*'"
)
print('application_root:', stdout5.read().decode(errors='replace').strip())

# Test welcome page
stdin6, stdout6, stderr6 = ssh.exec_command(
    'curl -s -o /dev/null -w "%{http_code}" https://vectornode.ru/superset/welcome/'
)
print('Welcome page:', stdout6.read().decode(errors='replace').strip())

ssh.close()
