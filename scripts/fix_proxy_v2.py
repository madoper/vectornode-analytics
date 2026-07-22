import paramiko, base64

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

# Read the config
stdin, stdout, stderr = ssh.exec_command('docker exec podft-superset cat /app/pythonpath/superset_config.py')
cfg = stdout.read().decode('utf-8', errors='replace')

# Fix the PROXY_FIX_CONFIG line
cfg = cfg.replace(
    'PROXY_FIX_CONFIG = {"x_for": 1, "x_proto": 1, "x_host": 1, "x_port": 1}',
    'PROXY_FIX_CONFIG = {"x_for": 1, "x_proto": 1, "x_host": 1, "x_port": 1, "x_prefix": 1}'
)

# Write to temp file on host, then docker cp
cfg_b64 = base64.b64encode(cfg.encode()).decode()
stdin2, stdout2, stderr2 = ssh.exec_command(
    f'echo {cfg_b64} | base64 -d > /tmp/superset_config.py && docker cp /tmp/superset_config.py podft-superset:/app/pythonpath/superset_config.py 2>&1'
)
print('Copy result:', stdout2.read().decode(errors='replace').strip())
err = stderr2.read().decode(errors='replace').strip()
if err:
    print('ERROR:', err[:300])

# Verify
stdin3, stdout3, stderr3 = ssh.exec_command('docker exec podft-superset grep PROXY_FIX /app/pythonpath/superset_config.py')
print('After fix:', stdout3.read().decode(errors='replace').strip())

# Restart Superset
stdin4, stdout4, stderr4 = ssh.exec_command('docker restart podft-superset 2>&1')
print('Restart:', stdout4.read().decode(errors='replace').strip())

import time
time.sleep(10)

# Test web login
stdin5, stdout5, stderr5 = ssh.exec_command(
    "curl -s -D - -o /dev/null -X POST https://vectornode.ru/superset/login/ "
    "-d 'username=admin&password=admin' "
    "-H 'Content-Type: application/x-www-form-urlencoded' "
    "-H 'Referer: https://vectornode.ru/superset/login/' 2>&1 | head -10"
)
print('\nWeb login result:')
print(stdout5.read().decode(errors='replace').strip())

# Also check if form action is now /superset/login
stdin6, stdout6, stderr6 = ssh.exec_command(
    "curl -s https://vectornode.ru/superset/login/ 2>&1 | grep -oE 'action=\"[^\"]*\"' | head -5"
)
print('\nForm actions:', stdout6.read().decode(errors='replace').strip())

ssh.close()
