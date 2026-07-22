import paramiko, json

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

cmds = [
    # Check what cookies we get from login
    '''curl -s -v -c /tmp/sc.txt -X POST http://127.0.0.1:8088/api/v1/security/login \
    -H "Content-Type: application/json" \
    -d '{"username":"admin","password":"admin","provider":"db"}' 2>&1 | grep -i "Set-Cookie"''',
    
    # Read the cookie file
    'cat /tmp/sc.txt 2>/dev/null',
]

for cmd in cmds:
    print(f'> {cmd[:80]}')
    stdin, stdout, stderr = ssh.exec_command(cmd)
    print(stdout.read().decode(errors='replace').strip()[:500])

ssh.close()
