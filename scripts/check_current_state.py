import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

cmds = [
    'docker ps --filter name=superset --format "{{.Names}} {{.Status}}"',
    'curl -s -o /dev/null -w "%{http_code}" https://vectornode.ru/superset/login/',
    "curl -s https://vectornode.ru/superset/login/ 2>&1 | grep -oP 'user_login_url[^,}]*|user_logout_url[^,}]*|user_info_url[^,}]*|application_root[^,}]*|brand.*?path[^,}]*' | head -10",
    "curl -s https://vectornode.ru/superset/login/ 2>&1 | grep -c 'fixBootstrap\\|DOMContentLoaded'",
    # Test login via API
    "curl -s -X POST https://vectornode.ru/superset/api/v1/security/login -H 'Content-Type: application/json' -d '{\"username\":\"admin\",\"password\":\"admin\",\"provider\":\"db\"}' | grep -o 'access_token' | head -1",
]

for cmd in cmds:
    stdin, stdout, stderr = ssh.exec_command(cmd)
    print(stdout.read().decode(errors='replace').strip()[:300])

ssh.close()
