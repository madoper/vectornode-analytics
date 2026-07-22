import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

# Get exact bytes around user_login_url  
stdin, stdout, stderr = ssh.exec_command(
    "curl -s https://vectornode.ru/superset/login/ 2>&1 | grep -oP '.{0,50}user_login_url.{0,50}'"
)
print('Raw bytes:')
print(stdout.read().decode(errors='replace').strip())

# Check if sub_filter is working at all - check service-worker pattern
stdin2, stdout2, stderr2 = ssh.exec_command(
    "curl -s https://vectornode.ru/superset/login/ 2>&1 | grep -o 'serviceWorker' | head -5"
)
print('\nserviceWorker in HTML:', stdout2.read().decode(errors='replace').strip())

ssh.close()
