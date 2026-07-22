import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

# Get Superset login page
stdin, stdout, stderr = ssh.exec_command(
    "curl -s https://vectornode.ru/superset/login/ | grep -o 'user_login_url[^,]*' | head -3"
)
print('user_login_url:', stdout.read().decode(errors='replace').strip())

# Test the /login/ fallback brings up a Superset page (not web-frontend)
stdin2, stdout2, stderr2 = ssh.exec_command(
    "curl -s https://vectornode.ru/login/ | grep -o '<title>[^<]*</title>' | head -3"
)
print('/login/ title:', stdout2.read().decode(errors='replace').strip())

# Check what /login/ serves (first 500 chars)
stdin3, stdout3, stderr3 = ssh.exec_command(
    "curl -s https://vectornode.ru/login/ | head -20"
)
print('/login/ HTML:')
print(stdout3.read().decode(errors='replace').strip()[:500])

ssh.close()
