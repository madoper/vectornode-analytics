import paramiko, base64

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

# Remove APPLICATION_ROOT from config
stdin, stdout, stderr = ssh.exec_command('cat /opt/podft/infra/superset-init/superset_config.py')
cfg = stdout.read().decode('utf-8', errors='replace')
cfg = cfg.replace("APPLICATION_ROOT = \"/superset\"\n", '')

cfg_b64 = base64.b64encode(cfg.encode()).decode()
stdin2, stdout2, stderr2 = ssh.exec_command(
    f'echo {cfg_b64} | base64 -d > /opt/podft/infra/superset-init/superset_config.py && echo OK'
)
print('Write:', stdout2.read().decode(errors='replace').strip())

# Restart Superset
ssh.exec_command('docker restart podft-superset')
print('Restarted Superset')

import time
time.sleep(15)

# Check health
stdin3, stdout3, stderr3 = ssh.exec_command(
    'docker ps --filter name=superset --format "{{.Names}} {{.Status}}"'
)
print('Status:', stdout3.read().decode(errors='replace').strip())

# Test login page
stdin4, stdout4, stderr4 = ssh.exec_command(
    'curl -s -o /dev/null -w "%{http_code}" https://vectornode.ru/superset/login/'
)
print('Login page:', stdout4.read().decode(errors='replace').strip())

# Check bootstrap data for user_login_url
stdin5, stdout5, stderr5 = ssh.exec_command(
    "curl -s https://vectornode.ru/superset/login/ 2>&1 | grep -oP 'user_login_url[^,}]*'"
)
print('user_login_url:', stdout5.read().decode(errors='replace').strip())

ssh.close()
