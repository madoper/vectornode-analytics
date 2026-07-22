import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', port=22, username='root', password='8884&JKL%f75', timeout=10)

# Check cache_manager filter_state_cache initialization
cmd = 'docker exec podft-superset grep -A30 "_filter_state_cache\|filter_state_cache = " /app/superset/utils/cache_manager.py 2>/dev/null | head -40'
_, o, _ = ssh.exec_command(cmd)
print('Cache manager init:')
print(o.read().decode(errors='replace'))

# Check SupersetMetastoreCache resource naming
cmd2 = 'docker exec podft-superset grep -n "resource\|RESOURCE\|CACHE_KEY_PREFIX\|namespace" /app/superset/cache_utils/metastore_cache.py 2>/dev/null | head -20'
_, o2, _ = ssh.exec_command(cmd2)
print('\nMetastoreCache resource info:')
print(o2.read().decode(errors='replace'))

ssh.close()
