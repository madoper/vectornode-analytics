import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', port=22, username='root', password='8884&JKL%f75', timeout=10)

# Read FILTER_STATE_CACHE_CONFIG from config
cmd = 'docker exec podft-superset python3 -c "from superset.config import FILTER_STATE_CACHE_CONFIG; import json; print(json.dumps(FILTER_STATE_CACHE_CONFIG, indent=2, default=str))"'
_, o, _ = ssh.exec_command(cmd)
print('FILTER_STATE_CACHE_CONFIG:')
print(o.read().decode(errors='replace'))

# Also check how filter_state_cache is configured
cmd2 = 'docker exec podft-superset cat /app/superset/utils/cache_manager.py 2>/dev/null | grep -A20 "filter_state"'
_, o2, _ = ssh.exec_command(cmd2)
print('\nCache manager filter_state:')
print(o2.read().decode(errors='replace'))

# Try to get filter state via Python inside container
cmd3 = "docker exec podft-superset python3 -c 'from superset.extensions import cache_manager; from superset.temporary_cache.utils import cache_key; k=cache_key(2, chr(34)+chr(34)); v=cache_manager.filter_state_cache.get(k); print(repr(v))' 2>&1"
_, o3, _ = ssh.exec_command(cmd3)
print('Filter state from cache:', o3.read().decode(errors='replace'))

ssh.close()
