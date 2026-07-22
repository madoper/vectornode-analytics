import paramiko, json

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

# Login via API and save cookies
stdin, stdout, stderr = ssh.exec_command(
    "curl -s -c /tmp/sup_cookies.txt -X POST https://vectornode.ru/superset/api/v1/security/login "
    "-H 'Content-Type: application/json' "
    "-d '{\"username\":\"admin\",\"password\":\"admin\",\"provider\":\"db\"}'"
)
print('API login:', stdout.read().decode(errors='replace').strip()[:100])

# Now with the session cookie, try accessing the welcome page
stdin2, stdout2, stderr2 = ssh.exec_command(
    "curl -s -o /dev/null -w '%{http_code}' -b /tmp/sup_cookies.txt https://vectornode.ru/superset/welcome/"
)
print('Welcome page:', stdout2.read().decode(errors='replace').strip())

# Also check the API token info
stdin3, stdout3, stderr3 = ssh.exec_command(
    "curl -s -b /tmp/sup_cookies.txt https://vectornode.ru/superset/api/v1/me/"
)
print('Me API:', stdout3.read().decode(errors='replace').strip()[:200])

ssh.close()
