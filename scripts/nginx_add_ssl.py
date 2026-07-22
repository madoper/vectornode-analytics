import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

sftp = ssh.open_sftp()
with sftp.open('/etc/nginx/sites-enabled/vectornode.ru', 'r') as f:
    cfg = f.read().decode('utf-8', errors='replace')

# Find the HTTP-only subdomain blocks and add SSL
old = b'''# === Airflow UI ===
server {
    listen 80;
    server_name admin.vectornode.ru;
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

# === Superset BI ===
server {
    listen 80;
    server_name bi.vectornode.ru;
    client_max_body_size 50m;
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

new = b'''# === Airflow UI ===
server {
    listen 80;
    server_name admin.vectornode.ru;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name admin.vectornode.ru;
    ssl_certificate /etc/letsencrypt/live/vectornode.ru/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/vectornode.ru/privkey.pem;
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

# === Superset BI ===
server {
    listen 80;
    server_name bi.vectornode.ru;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name bi.vectornode.ru;
    ssl_certificate /etc/letsencrypt/live/vectornode.ru/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/vectornode.ru/privkey.pem;
    client_max_body_size 50m;
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

cfg = cfg.encode('utf-8').replace(old, new)

with sftp.open('/etc/nginx/sites-enabled/vectornode.ru', 'w') as f:
    f.write(cfg)

stdin, stdout, stderr = ssh.exec_command('nginx -t 2>&1 && systemctl reload nginx 2>&1')
print(stdout.read().decode(errors='replace').strip())

# Test curl to the domains
import time
time.sleep(2)
stdin2, stdout2, stderr2 = ssh.exec_command(
    "curl -s -o /dev/null -w '%{http_code}' http://admin.vectornode.ru/ 2>&1"
)
print(f'admin HTTP: {stdout2.read().decode(errors="replace").strip()}')

stdin3, stdout3, stderr3 = ssh.exec_command(
    "curl -s -o /dev/null -w '%{http_code}' https://admin.vectornode.ru/ 2>&1"
)
print(f'admin HTTPS: {stdout3.read().decode(errors="replace").strip()}')

stdin4, stdout4, stderr4 = ssh.exec_command(
    "curl -s -o /dev/null -w '%{http_code}' http://bi.vectornode.ru/ 2>&1"
)
print(f'bi HTTP: {stdout4.read().decode(errors="replace").strip()}')

ssh.close()
