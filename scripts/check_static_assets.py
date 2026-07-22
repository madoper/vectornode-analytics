import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

# Check static assets
cmds = [
    # Check CSS files
    "curl -s -o /dev/null -w '%{http_code}' https://vectornode.ru/superset/static/assets/8706.6dfab372988d20453152.entry.css",
    # Check JS files
    "curl -s -o /dev/null -w '%{http_code}' https://vectornode.ru/superset/static/assets/vendors.6f4ecbc3d2e23e236060.entry.js",
    # Check direct health
    "curl -s http://127.0.0.1:8088/static/assets/8706.6dfab372988d20453152.entry.css -o /dev/null -w '%{http_code}'",
    # Check if the login page form action is correct  
    "curl -s https://vectornode.ru/superset/login/ 2>&1 | grep -oE 'action=\"[^\"]*\"' | head -5",
    # Check the full <head> section with injection
    "curl -s https://vectornode.ru/superset/login/ 2>&1 | head -5",
]

for cmd in cmds:
    stdin, stdout, stderr = ssh.exec_command(cmd)
    print(stdout.read().decode(errors='replace').strip())

ssh.close()
