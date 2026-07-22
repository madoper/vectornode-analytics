import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

# Read the config file
stdin, stdout, stderr = ssh.exec_command('docker exec podft-superset cat /app/pythonpath/superset_config.py')
cfg_content = stdout.read().decode('utf-8', errors='replace')
print('Current config:')
print(cfg_content)

# Fix the PROXY_FIX_CONFIG line
cfg_content = cfg_content.replace(
    'PROXY_FIX_CONFIG = {"x_for": 1, "x_proto": 1, "x_host": 1, "x_port": 1}',
    'PROXY_FIX_CONFIG = {"x_for": 1, "x_proto": 1, "x_host": 1, "x_port": 1, "x_prefix": 1}'
)

# Write back via heredoc
import json
cfg_escaped = cfg_content.replace('"', '\\"').replace("'", "'\\''")
# Actually, let's use base64 to avoid escaping issues
import base64
cfg_b64 = base64.b64encode(cfg_content.encode()).decode()

cmd = f'docker exec podft-superset sh -c "echo {cfg_b64} | base64 -d > /app/pythonpath/superset_config.py"'
stdin2, stdout2, stderr2 = ssh.exec_command(cmd)
print('\nWrite result:', stdout2.read().decode(errors='replace').strip())
print('Errors:', stderr2.read().decode(errors='replace').strip()[:200])

# Verify
stdin3, stdout3, stderr3 = ssh.exec_command('docker exec podft-superset grep PROXY_FIX /app/pythonpath/superset_config.py')
print('After update:', stdout3.read().decode(errors='replace').strip())

ssh.close()
