import paramiko, base64

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

# Read the current config
stdin, stdout, stderr = ssh.exec_command('cat /opt/podft/infra/superset-init/superset_config.py')
cfg = stdout.read().decode('utf-8', errors='replace')
print('Current config:')
print(cfg)

# Add APPLICATION_ROOT and update PROXY_FIX_CONFIG
cfg += '\nAPPLICATION_ROOT = "/superset"\n'
cfg = cfg.replace(
    'PROXY_FIX_CONFIG = {"x_for": 1, "x_proto": 1, "x_host": 1, "x_port": 1}',
    'PROXY_FIX_CONFIG = {"x_for": 1, "x_proto": 1, "x_host": 1, "x_port": 1, "x_prefix": 1}'
)

# Write back via base64
cfg_b64 = base64.b64encode(cfg.encode()).decode()
stdin2, stdout2, stderr2 = ssh.exec_command(
    f'echo {cfg_b64} | base64 -d > /opt/podft/infra/superset-init/superset_config.py && echo OK || echo FAIL'
)
print('\nWrite result:', stdout2.read().decode(errors='replace').strip())

# Verify
stdin3, stdout3, stderr3 = ssh.exec_command('cat /opt/podft/infra/superset-init/superset_config.py')
print('Updated config:')
print(stdout3.read().decode(errors='replace').strip())

ssh.close()
