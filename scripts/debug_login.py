import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

# Check if the login page has a form with action
stdin, stdout, stderr = ssh.exec_command(
    "curl -s https://vectornode.ru/superset/login/ 2>&1 | grep -i 'action\\|form' | head -10"
)
print('Form/action in HTML:')
print(stdout.read().decode(errors='replace').strip())

# Check the full login page structure
stdin2, stdout2, stderr2 = ssh.exec_command(
    "curl -s https://vectornode.ru/superset/login/ 2>&1 | head -30"
)
print('\nFirst 30 lines of login page:')
print(stdout2.read().decode(errors='replace').strip()[:1500])

# Check content-type header
stdin3, stdout3, stderr3 = ssh.exec_command(
    "curl -sI https://vectornode.ru/superset/login/ 2>&1 | grep -i content-type"
)
print('\nContent-Type:', stdout3.read().decode(errors='replace').strip())

# Also check what's at /login/ (the wrong redirect target)
stdin4, stdout4, stderr4 = ssh.exec_command(
    "curl -s -o /dev/null -w '%{http_code}' https://vectornode.ru/login/ 2>&1"
)
print('/login/ HTTP:', stdout4.read().decode(errors='replace').strip())

ssh.close()
