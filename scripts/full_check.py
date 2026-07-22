import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

# Full verification
cmds = [
    "echo '=== Superset status ==='",
    'docker ps --filter name=superset --format "{{.Names}} {{.Status}}"',
    "echo '=== Login page ==='",
    'curl -s -o /dev/null -w "%{http_code}" https://vectornode.ru/superset/login/',
    "echo '=== /login/ returns ==='",
    'curl -s -o /dev/null -w "%{http_code}" https://vectornode.ru/login/',
    "echo '=== API login ==='",
    "curl -s -X POST https://vectornode.ru/superset/api/v1/security/login -H 'Content-Type: application/json' -d '{\"username\":\"admin\",\"password\":\"admin\",\"provider\":\"db\"}' | grep -o 'access_token' | head -1",
    "echo '=== /user_info/ ==='",
    'curl -s -o /dev/null -w "%{http_code}" https://vectornode.ru/user_info/',
    "echo '=== Service Worker ==='",
    'curl -s -o /dev/null -w "%{http_code}" https://vectornode.ru/static/service-worker.js',
    "echo '=== Injection present ==='",
    "curl -s https://vectornode.ru/superset/login/ 2>&1 | grep -c '_fixSS'",
]

for cmd in cmds:
    stdin, stdout, stderr = ssh.exec_command(cmd)
    print(stdout.read().decode(errors='replace').strip())

ssh.close()
