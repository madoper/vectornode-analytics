import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', port=22, username='root', password='8884&JKL%f75', timeout=10)

# Find filter_state_cache config
cmds = [
    'docker exec podft-superset grep -rn "FILTER_STATE_CACHE_CONFIG\\|filter_state_cache\\|CACHE_KEY_PREFIX" /app/superset/config.py 2>/dev/null | head -20',
    'docker exec podft-superset grep -rn "FILTER_STATE_CACHE_CONFIG" /app/superset/ 2>/dev/null | head -15',
    # Try to get filter state from Redis with known key format
    'docker exec podft-redis redis-cli --raw GET "2;on3j7Uo8xSs" 2>/dev/null; echo "---"',
    'docker exec podft-redis redis-cli --raw GET "filter_state;2;on3j7Uo8xSs" 2>/dev/null; echo "---"',
    'docker exec podft-redis redis-cli --raw GET "superset_filter_state_2;on3j7Uo8xSs" 2>/dev/null; echo "---"',
]
for cmd in cmds:
    _, o, _ = ssh.exec_command(cmd)
    out = o.read().decode(errors='replace')
    if out.strip() and 'END' not in out:
        print(out)
        print('===')

ssh.close()
