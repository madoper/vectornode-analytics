import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

sftp = ssh.open_sftp()
with sftp.open('/etc/nginx/sites-enabled/vectornode.ru', 'r') as f:
    cfg = f.read()

# Add no-op Service Worker to bi.vectornode.ru server block
# Find the location / block inside the bi.vectornode.ru HTTPS server
old = b'''# === Superset BI ===
server {
    listen 80;
    server_name bi.vectornode.ru;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name bi.vectornode.ru;
    ssl_certificate /etc/letsencrypt/live/admin.vectornode.ru/fullchain.pem; # managed by Certbot
    ssl_certificate_key /etc/letsencrypt/live/admin.vectornode.ru/privkey.pem; # managed by Certbot
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
}'''

new = b'''# === Superset BI ===
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
}'''

cfg = cfg.replace(old, new)

with sftp.open('/etc/nginx/sites-enabled/vectornode.ru', 'w') as f:
    f.write(cfg)

stdin, stdout, stderr = ssh.exec_command('nginx -t 2>&1 && systemctl reload nginx 2>&1')
print('Nginx:', stdout.read().decode(errors='replace').strip())

# Verify
import time
time.sleep(2)
stdin2, stdout2, stderr2 = ssh.exec_command('curl -s -o /dev/null -w "%{http_code}" https://bi.vectornode.ru/static/service-worker.js 2>&1')
print(f'Service Worker: {stdout2.read().decode(errors="replace").strip()}')

ssh.close()
