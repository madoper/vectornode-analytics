import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

# Check static assets paths referenced in the login page
cmd = "curl -s https://vectornode.ru/superset/login/ 2>&1 | grep -oE 'href=\"[^\"]*static[^\"]*\"' | head -5"
stdin, stdout, stderr = ssh.exec_command(cmd)
print('Static assets in login page:')
print(stdout.read().decode(errors='replace').strip())

# Test the service worker directly
cmd2 = 'curl -sI https://vectornode.ru/static/service-worker.js 2>&1 | head -10'
stdin2, stdout2, stderr2 = ssh.exec_command(cmd2)
print('\nService Worker headers:')
print(stdout2.read().decode(errors='replace').strip())

# Try API login + get a page without CSRF redirect issue
cmd3 = ("curl -s https://vectornode.ru/superset/login/ 2>&1 | grep -oE 'src=\"[^\"]*static[^\"]*\"' | head -5")
stdin3, stdout3, stderr3 = ssh.exec_command(cmd3)
print('\nScripts in login page:')
print(stdout3.read().decode(errors='replace').strip())

ssh.close()
