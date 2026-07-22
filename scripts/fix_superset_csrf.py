import paramiko, base64

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

# Read current config
stdin, stdout, stderr = ssh.exec_command('cat /opt/podft/infra/superset-init/superset_config.py')
cfg = stdout.read().decode()

# Add WTF_CSRF_EXEMPT_LIST to exempt chart data endpoint
cfg += '\nWTF_CSRF_EXEMPT_LIST = ["/api/v1/chart/data"]\n'

# Write back via base64
cfg_b64 = base64.b64encode(cfg.encode()).decode()
stdin2, stdout2, stderr2 = ssh.exec_command(
    f'echo {cfg_b64} | base64 -d > /opt/podft/infra/superset-init/superset_config.py && echo OK'
)
print('Write:', stdout2.read().decode(errors='replace').strip())

# Verify
stdin3, stdout3, stderr3 = ssh.exec_command('grep "CSRF_EXEMPT" /opt/podft/infra/superset-init/superset_config.py')
print('Config:', stdout3.read().decode(errors='replace').strip())

# Restart Superset
stdin4, stdout4, stderr4 = ssh.exec_command('docker restart podft-superset 2>&1')
print('Restart:', stdout4.read().decode(errors='replace').strip())

import time
time.sleep(15)

# Test health
stdin5, stdout5, stderr5 = ssh.exec_command('curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8088/health')
print('Health:', stdout5.read().decode(errors='replace').strip())

ssh.close()
