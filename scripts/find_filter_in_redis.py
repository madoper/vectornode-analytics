import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', port=22, username='root', password='8884&JKL%f75', timeout=10)

# Check the actual cache key format used
# Read the default config for FILTER_STATE_CACHE_CONFIG
cmd = 'docker exec podft-superset cat /app/superset/config.py | grep -A10 "FILTER_STATE_CACHE_CONFIG" | head -15'
_, o, _ = ssh.exec_command(cmd)
print('FILTER_STATE_CACHE_CONFIG source:')
print(o.read().decode(errors='replace'))

# Try Redis keys with different prefixes
cmd2 = 'docker exec podft-redis redis-cli KEYS "*2;*" 2>/dev/null'
_, o2, _ = ssh.exec_command(cmd2)
print('\nRedis keys with 2:')
print(o2.read().decode(errors='replace'))

# Try with SCAN
cmd3 = 'docker exec podft-redis redis-cli --scan --pattern "*filter*" 2>/dev/null'
_, o3, _ = ssh.exec_command(cmd3)
print('\nRedis SCAN filter:')
print(o3.read().decode(errors='replace'))

# Try SCAN for dashboard
cmd4 = 'docker exec podft-redis redis-cli --scan --pattern "*dashboard*" 2>/dev/null'
_, o4, _ = ssh.exec_command(cmd4)
print('\nRedis SCAN dashboard:')
print(o4.read().decode(errors='replace'))

ssh.close()
