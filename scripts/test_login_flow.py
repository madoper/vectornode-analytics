import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

# Test if /login/ serves the Superset login properly
stdin, stdout, stderr = ssh.exec_command(
    "curl -s https://vectornode.ru/login/ 2>&1 | grep -c 'Superset'"
)
print('Superset mentions on /login/:', stdout.read().decode(errors='replace').strip())

# Check raw bootstrap data for login url
stdin2, stdout2, stderr2 = ssh.exec_command(
    "curl -s https://vectornode.ru/superset/login/ 2>&1 | grep -oP 'user_login_url[^,}]*'"
)
print('\nuser_login_url raw:', stdout2.read().decode(errors='replace').strip())

# Test full web login flow through /login/
stdin3, stdout3, stderr3 = ssh.exec_command(
    "curl -s -D - -c /tmp/sup_test.txt -X POST https://vectornode.ru/login/ "
    "-d 'username=admin&password=admin' "
    "-H 'Content-Type: application/x-www-form-urlencoded' "
    "-H 'Referer: https://vectornode.ru/login/' 2>&1 | head -15"
)
print('\n/login/ POST result:')
print(stdout3.read().decode(errors='replace').strip())

# Also test through /superset/login/ with CSRF token
stdin4, stdout4, stderr4 = ssh.exec_command(
    "curl -s https://vectornode.ru/superset/login/ 2>&1 | grep CSRF || grep -i 'csrf_token'"
)
print('\nCSRF check:', stdout4.read().decode(errors='replace').strip()[:500])

ssh.close()
