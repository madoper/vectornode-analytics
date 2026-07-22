import paramiko, time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

# Check superset status
stdin, stdout, stderr = ssh.exec_command('docker ps --filter name=superset --format "{{.Names}} {{.Status}}"')
print('Superset:', stdout.read().decode(errors='replace').strip())

# Check the ProxyFix config
stdin2, stdout2, stderr2 = ssh.exec_command(
    "docker exec podft-superset cat /app/pythonpath/superset_config.py | grep PROXY_FIX"
)
print('Proxy config:', stdout2.read().decode(errors='replace').strip())

time.sleep(10)

# Test web login again
stdin3, stdout3, stderr3 = ssh.exec_command(
    "curl -s -D - -o /dev/null -X POST https://vectornode.ru/superset/login/ "
    "-d 'username=admin&password=admin' "
    "-H 'Content-Type: application/x-www-form-urlencoded' "
    "-H 'Referer: https://vectornode.ru/superset/login/' 2>&1 | head -15"
)
print('\nWeb login test:')
print(stdout3.read().decode(errors='replace').strip())

# Check if the login page loads correctly
stdin4, stdout4, stderr4 = ssh.exec_command(
    "curl -s https://vectornode.ru/superset/login/ | grep -oE 'action=\"[^\"]*\"' | head -5"
)
print('\nForm actions in login page:')
print(stdout4.read().decode(errors='replace').strip())

ssh.close()
