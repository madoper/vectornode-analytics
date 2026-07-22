import paramiko, time
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', port=22, username='root', password='8884&JKL%f75', timeout=15)

# 1. Fix superset_config.py on the host mount
sftp = ssh.open_sftp()
sftp.put(r'D:\project\FRS_TEST\scripts\superset_config_clean.py', '/opt/podft/infra/superset-init/superset_config.py')
sftp.close()
print('1. superset_config.py fixed')

# 2. Clean Docker volume
V = '/var/lib/docker/volumes/podft_superset_data/_data'
ssh.exec_command(f'rm -f {V}/fix_chart_patch.py {V}/fix_chart_api.py 2>/dev/null')
ssh.exec_command(f'find {V} -name "*.pyc" -delete 2>/dev/null; find {V} -name "__pycache__" -exec rm -rf {{}} + 2>/dev/null')
print('2. Volume cleaned')

# 3. Fix Nginx - remove map and chart/data redirect
import urllib.parse
nginx_conf = '''# pod-ft VPS nginx config
upstream gateway {
    server localhost:8000;
}

upstream web_frontend {
    server localhost:8080;
}

server {
    listen 80;
    server_name vectornode.ru www.vectornode.ru;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name vectornode.ru www.vectornode.ru;

    ssl_certificate /etc/letsencrypt/live/vectornode.ru/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/vectornode.ru/privkey.pem;

    location /api/v1/ {
        proxy_pass http://127.0.0.1:8088/api/v1/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $host;
    }

    location /api/ {
        proxy_pass http://gateway;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /health {
        proxy_pass http://gateway;
        proxy_set_header Host $host;
    }

    location /superset/ {
        proxy_pass http://127.0.0.1:8088/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $host;
        proxy_redirect / /superset/;
        proxy_connect_timeout 300s;
        proxy_read_timeout 300s;
        proxy_send_timeout 300s;
        client_max_body_size 50m;
    }

    location /superset/log/ {
        limit_except POST { deny all; }
        return 204;
    }

    location /superset/static/ {
        proxy_pass http://127.0.0.1:8088/static/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_buffering off;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    location = /static/service-worker.js {
        add_header Content-Type application/javascript;
        add_header Service-Worker-Allowed /;
        return 200 "self.addEventListener('install',()=>self.skipWaiting());self.addEventListener('activate',()=>self.clients.claim());";
    }

    location /static/ {
        proxy_pass http://127.0.0.1:8088/static/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_buffering off;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    location / {
        proxy_pass http://web_frontend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

server {
    listen 80;
    server_name admin.vectornode.ru;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name admin.vectornode.ru;
    ssl_certificate /etc/letsencrypt/live/admin.vectornode.ru/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/admin.vectornode.ru/privkey.pem;
    client_max_body_size 20m;
    location / {
        proxy_pass http://127.0.0.1:8081;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}

server {
    listen 80;
    server_name bi.vectornode.ru;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name bi.vectornode.ru;
    ssl_certificate /etc/letsencrypt/live/admin.vectornode.ru/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/admin.vectornode.ru/privkey.pem;
    client_max_body_size 50m;

    location = /static/service-worker.js {
        add_header Content-Type application/javascript;
        add_header Service-Worker-Allowed /;
        return 200 "self.addEventListener('install',()=>self.skipWaiting());self.addEventListener('activate',()=>self.clients.claim());";
    }

    location / {
        proxy_pass http://127.0.0.1:8088;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $host;
        proxy_connect_timeout 300s;
        proxy_read_timeout 300s;
        proxy_send_timeout 300s;
    }
}
'''

sftp2 = ssh.open_sftp()
f = sftp2.file('/etc/nginx/sites-available/podft', 'w')
f.write(nginx_conf)
f.close()
sftp2.close()

# Also save locally for reference
with open(r'D:\project\FRS_TEST\nginx\vectornode.conf', 'w') as fw:
    fw.write(nginx_conf)

# Test and reload Nginx
_, no, _ = ssh.exec_command('nginx -t 2>&1')
result = no.read().decode(errors='replace').strip()
print('3. Nginx -t:', result)
if 'successful' in result:
    _, no2, _ = ssh.exec_command('nginx -s reload 2>&1')
    print('   Nginx reloaded')
else:
    print('   Nginx config error!')

# 4. Restart Superset
_, so, _ = ssh.exec_command('docker restart podft-superset 2>&1')
print('4. Superset restarting...')
time.sleep(30)

# 5. Check status
_, so2, _ = ssh.exec_command('docker ps --filter name=podft-superset --format "{{.Status}}"')
print('5. Status:', so2.read().decode(errors='replace').strip())

# Check for errors
_, so3, _ = ssh.exec_command('docker logs podft-superset --since 1m 2>&1 | grep -i "error\|traceback\|syntax" | tail -5')
errors = so3.read().decode(errors='replace').strip()
print('   Errors:', errors if errors else 'NONE')

# 6. Verify version
time.sleep(10)
_, so4, _ = ssh.exec_command('docker exec podft-superset superset version 2>&1')
print('6. Version:', so4.read().decode(errors='replace')[:100])

ssh.close()
