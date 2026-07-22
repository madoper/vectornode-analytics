import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

# Get the login page HTML and check for service worker registration
cmd = "curl -s https://vectornode.ru/superset/login/ 2>&1 | grep -i 'serviceWorker\\|service-worker\\|navigator' | head -5"
stdin, stdout, stderr = ssh.exec_command(cmd)
print('Service Worker references in HTML:')
print(stdout.read().decode(errors='replace').strip())

# Try to login via the webform 
cmd2 = """curl -s -D - -c /tmp/ss_test.txt -X POST https://vectornode.ru/superset/login/ \
  -d "username=admin&password=admin" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -H "Referer: https://vectornode.ru/superset/login/" 2>&1 | head -20"""
stdin2, stdout2, stderr2 = ssh.exec_command(cmd2)
print('\nLogin attempt:')
print(stdout2.read().decode(errors='replace').strip()[:500])

ssh.close()
