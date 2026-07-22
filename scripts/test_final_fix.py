import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

cmds = [
    # Test login page
    'curl -s -o /dev/null -w "%{http_code}" https://vectornode.ru/superset/login/',
    # Test welcome page
    'curl -s -o /dev/null -w "%{http_code}" https://vectornode.ru/superset/welcome/',
    # Test API
    'curl -s -X POST https://vectornode.ru/superset/api/v1/security/login -H "Content-Type: application/json" -d \'{"username":"admin","password":"admin","provider":"db"}\' | grep -o "access_token" | head -1',
    # Test datasets API
    'curl -s -H "Authorization: Bearer $(curl -s -X POST https://vectornode.ru/superset/api/v1/security/login -H \'Content-Type: application/json\' -d \'{\"username\":\"admin\",\"password\":\"admin\",\"provider\":\"db\"}\' | python3 -c \"import sys,json;print(json.load(sys.stdin)[\\\"access_token\\\"])\")" https://vectornode.ru/superset/api/v1/dataset/ | python3 -c "import sys,json;d=json.load(sys.stdin);print(f\'Datasets: {d.get(\\\"count\\\",0)}\')"',
]

for cmd in cmds:
    stdin, stdout, stderr = ssh.exec_command(cmd)
    print(stdout.read().decode(errors='replace').strip()[:200])

ssh.close()
