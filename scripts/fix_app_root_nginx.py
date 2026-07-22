import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

# 1. Fix Nginx config - remove broken $dq rules
sftp = ssh.open_sftp()
with sftp.open('/etc/nginx/sites-enabled/vectornode.ru', 'r') as f:
    cfg = f.read().decode('utf-8', errors='replace')

old = '''        sub_filter '$dq/user_info/$dq' '$dq/superset/user_info/$dq';
        sub_filter '$dqapplication_root$dq: $dq/$dq' '$dqapplication_root$dq: $dq/superset/$dq';'''

new = '''        sub_filter '"user_info_url":"' '"user_info_url":"/superset';
        sub_filter '"application_root":"' '"application_root":"/superset';'''

cfg = cfg.replace(old, new)

with sftp.open('/etc/nginx/sites-enabled/vectornode.ru', 'w') as f:
    f.write(cfg.encode())
sftp.close()

# Test and reload
stdin, stdout, stderr = ssh.exec_command('nginx -t 2>&1 && systemctl reload nginx 2>&1')
print('Nginx:', stdout.read().decode(errors='replace').strip())

# 2. Set APPLICATION_ROOT in superset config
import base64
stdin2, stdout2, stderr2 = ssh.exec_command('cat /opt/podft/infra/superset-init/superset_config.py')
cfg2 = stdout2.read().decode('utf-8', errors='replace')

cfg2 = cfg2.replace("PROXY_FIX_CONFIG = {\"x_for\": 1, \"x_proto\": 1, \"x_host\": 1, \"x_port\": 1, \"x_prefix\": 1}",
                     "PROXY_FIX_CONFIG = {\"x_for\": 1, \"x_proto\": 1, \"x_host\": 1, \"x_port\": 1, \"x_prefix\": 1}\nAPPLICATION_ROOT = \"/superset\"")

cfg_b64 = base64.b64encode(cfg2.encode()).decode()
stdin3, stdout3, stderr3 = ssh.exec_command(f'echo {cfg_b64} | base64 -d > /opt/podft/infra/superset-init/superset_config.py; echo OK')
print('Config write:', stdout3.read().decode(errors='replace').strip())

# Verify
stdin4, stdout4, stderr4 = ssh.exec_command('grep "APPLICATION_ROOT" /opt/podft/infra/superset-init/superset_config.py')
print('APPLICATION_ROOT:', stdout4.read().decode(errors='replace').strip())

# Restart Superset
stdin5, stdout5, stderr5 = ssh.exec_command('docker restart podft-superset 2>&1')
print('Restart:', stdout5.read().decode(errors='replace').strip())

# Check logs for errors
import time
time.sleep(20)

stdin6, stdout6, stderr6 = ssh.exec_command('docker logs podft-superset --tail 5 2>&1')
print('\nLogs:', stdout6.read().decode(errors='replace').strip())

# Check health
stdin7, stdout7, stderr7 = ssh.exec_command('curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8088/health')
print('Health:', stdout7.read().decode(errors='replace').strip())

# Check login page via Nginx
stdin8, stdout8, stderr8 = ssh.exec_command('curl -s -o /dev/null -w "%{http_code}" https://vectornode.ru/superset/login/')
print('Login:', stdout8.read().decode(errors='replace').strip())

# Check bootstrap data
stdin9, stdout9, stderr9 = ssh.exec_command(
    "curl -s https://vectornode.ru/superset/login/ 2>&1 | grep -oP 'application_root[^,}]*|user_info_url[^,}]*|user_login_url[^,}]*'"
)
print('\nBootstrap URLs:')
print(stdout9.read().decode(errors='replace').strip())

ssh.close()
