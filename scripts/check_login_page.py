import paramiko, time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

# Get a sample of the login page HTML
stdin, stdout, stderr = ssh.exec_command(
    "curl -s https://vectornode.ru/superset/login/ 2>&1 | tail -30"
)
print('Login page HTML (last 30 lines):')
print(stdout.read().decode(errors='replace').strip()[:2000])

# Check if the login page has form or is SPA
stdin2, stdout2, stderr2 = ssh.exec_command(
    "curl -s https://vectornode.ru/superset/login/ 2>&1 | grep -i 'form\\|login\\|csrf' | head -10"
)
print('\nForm/CSRF references:')
print(stdout2.read().decode(errors='replace').strip()[:1000])

# Update PROXY_FIX_CONFIG properly
stdin3, stdout3, stderr3 = ssh.exec_command(
    'docker exec podft-superset sh -c "echo PROXY_FIX_CONFIG = {\\"x_for\\": 1, \\"x_proto\\": 1, \\"x_host\\": 1, \\"x_port\\": 1, \\"x_prefix\\": 1} >> /app/pythonpath/superset_config.py && grep PROXY_FIX /app/pythonpath/superset_config.py | tail -1"'
)
print('\nProxy config update:', stdout3.read().decode(errors='replace').strip())

ssh.close()
