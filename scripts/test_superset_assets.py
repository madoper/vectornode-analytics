import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

cmds = [
    'curl -s -o /dev/null -w "%{http_code}" https://vectornode.ru/superset/login/',
    'curl -s https://vectornode.ru/superset/login/ 2>&1 | grep -o "serviceWorker" | head -3',
    'curl -s -o /dev/null -w "%{http_code}" https://vectornode.ru/superset/static/assets/',
    'curl -s http://127.0.0.1:8088/static/assets/app.css -o /dev/null -w "%{http_code}"',
    'curl -s -o /dev/null -w "%{http_code}" https://vectornode.ru/superset/static/assets/app.css',
]

for cmd in cmds:
    stdin, stdout, stderr = ssh.exec_command(cmd)
    print(stdout.read().decode(errors='replace').strip()[:200])

ssh.close()
