import paramiko, base64

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

# 1. Remove APPLICATION_ROOT from config
stdin, stdout, stderr = ssh.exec_command('cat /opt/podft/infra/superset-init/superset_config.py')
cfg = stdout.read().decode('utf-8', errors='replace')
cfg = cfg.replace('\nAPPLICATION_ROOT = "/superset"', '')
cfg_b64 = base64.b64encode(cfg.encode()).decode()
ssh.exec_command(f'echo {cfg_b64} | base64 -d > /opt/podft/infra/superset-init/superset_config.py')

# 2. Restart Superset
ssh.exec_command('docker restart podft-superset')

import time
time.sleep(20)

# 3. Add Nginx location for /user_info/
sftp = ssh.open_sftp()
with sftp.open('/etc/nginx/sites-enabled/vectornode.ru', 'r') as f:
    nginx_cfg = f.read().decode('utf-8', errors='replace')

# Find where /login/ location ends and add /user_info/ after it
old = '''    location /logout/ {
        proxy_pass http://127.0.0.1:8088/logout/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Prefix /superset;
    }'''

new = '''    location /logout/ {
        proxy_pass http://127.0.0.1:8088/logout/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Prefix /superset;
    }

    location /user_info/ {
        proxy_pass http://127.0.0.1:8088/user_info/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Prefix /superset;
    }'''

nginx_cfg = nginx_cfg.replace(old, new)

with sftp.open('/etc/nginx/sites-enabled/vectornode.ru', 'w') as f:
    f.write(nginx_cfg.encode())
sftp.close()

stdin2, stdout2, stderr2 = ssh.exec_command('nginx -t 2>&1 && systemctl reload nginx 2>&1')
print('Nginx:', stdout2.read().decode(errors='replace').strip())

# Test Superset
for url in [
    'https://vectornode.ru/superset/login/',
    'https://vectornode.ru/user_info/',
    'https://vectornode.ru/login/',
    'http://127.0.0.1:8088/health',
]:
    stdin3, stdout3, stderr3 = ssh.exec_command(f'curl -s -o /dev/null -w "%{{http_code}}" {url} 2>&1')
    print(f'{url}: {stdout3.read().decode(errors="replace").strip()}')

# Check bootstrap data
stdin4, stdout4, stderr4 = ssh.exec_command(
    "curl -s https://vectornode.ru/superset/login/ 2>&1 | grep -oP 'user_info_url[^,}]*|application_root[^,}]*'"
)
print(f'\nBootstrap: {stdout4.read().decode(errors="replace").strip()}')

ssh.close()
