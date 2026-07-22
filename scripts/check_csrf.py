import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

# Check for CSRF references in the login page
stdin, stdout, stderr = ssh.exec_command(
    "curl -s https://vectornode.ru/superset/login/ 2>&1 | grep -oi 'csrf\\|token' | head -10"
)
print('CSRF/Token refs:', stdout.read().decode(errors='replace').strip())

# Get full bootstrap data to find CSRF token
stdin2, stdout2, stderr2 = ssh.exec_command(
    "curl -s https://vectornode.ru/superset/login/ 2>&1 | grep -oP 'data-bootstrap=\"[^\"]*\"' | head -1"
)
bootstrap = stdout2.read().decode(errors='replace').strip()
print('\nBootstrap data (first 300 chars):')
print(bootstrap[:300])

# Try to get CSRF token via API  
stdin3, stdout3, stderr3 = ssh.exec_command(
    "curl -s -D - https://vectornode.ru/superset/api/v1/security/csrf_token/ 2>&1 | head -20"
)
print('\nCSRF token response:')
print(stdout3.read().decode(errors='replace').strip())

ssh.close()
