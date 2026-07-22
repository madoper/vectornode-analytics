import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', port=22, username='root', password='8884&JKL%f75', timeout=10)

# Check cache_key utility
cmds = [
    'docker exec podft-superset cat /app/superset/temporary_cache/utils.py 2>/dev/null',
    'docker exec podft-redis redis-cli KEYS "*" 2>/dev/null | head -30',
]
for cmd in cmds:
    _, o, _ = ssh.exec_command(cmd)
    print(o.read().decode(errors='replace'))
    print('===END===')

ssh.close()
