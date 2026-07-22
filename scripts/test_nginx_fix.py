import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

cmds = [
    'curl -s -o /dev/null -w "%{http_code}" https://vectornode.ru/superset/login/',
    'curl -s https://vectornode.ru/static/service-worker.js | head -5',
    'curl -s -o /dev/null -w "%{http_code}" https://vectornode.ru/superset/static/service-worker.js',
    'curl -s -o /dev/null -w "%{http_code}" https://vectornode.ru/static/assets/app.css',
]

for cmd in cmds:
    print(f'> {cmd[:70]}')
    stdin, stdout, stderr = ssh.exec_command(cmd)
    print(stdout.read().decode(errors='replace').strip()[:200])

ssh.close()
