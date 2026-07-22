import paramiko, time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

time.sleep(20)

cmds = [
    'docker ps --filter name=superset --format "{{.Names}} {{.Status}}"',
    'curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8088/health',
    'curl -s -o /dev/null -w "%{http_code}" https://vectornode.ru/superset/login/',
    "curl -s https://vectornode.ru/superset/login/ 2>&1 | grep -oP 'user_info_url[^,}]*|application_root[^,}]*'",
    'curl -s -o /dev/null -w "%{http_code}" https://vectornode.ru/user_info/',
    "curl -s https://vectornode.ru/user_info/ 2>&1 | grep -o 'User' | head -3",
]

for cmd in cmds:
    stdin, stdout, stderr = ssh.exec_command(cmd)
    res = stdout.read().decode(errors='replace').strip()
    print(res[:300])

ssh.close()
