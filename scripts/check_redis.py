import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', port=22, username='root', password='8884&JKL%f75', timeout=10)

# Check Redis for filter_state keys
cmds = [
    'docker exec podft-redis redis-cli KEYS "*filter_state*"',
    'docker exec podft-redis redis-cli KEYS "*dashboard*2*"',
    'docker exec podft-redis redis-cli KEYS "*on3j7*"',
    'docker exec podft-superset grep -rn "FILTER_STATE\\|filter_state_cache\\|CACHE_KEY" /app/superset/commands/dashboard/ 2>/dev/null | head -20',
]
for cmd in cmds:
    _, o, _ = ssh.exec_command(cmd)
    out = o.read().decode(errors='replace')
    if out.strip():
        print(out)
        print('---')

ssh.close()
