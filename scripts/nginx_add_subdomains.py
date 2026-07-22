import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

sftp = ssh.open_sftp()
with sftp.open('/etc/nginx/sites-enabled/vectornode.ru', 'r') as f:
    cfg = f.read().decode('utf-8', errors='replace')

# Add admin.vectornode.ru (Airflow) and bi.vectornode.ru (Superset) server blocks
# Insert AFTER the HTTP redirect block and BEFORE the HTTPS server block of the main domain
prepend = '''# === Airflow UI ===
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
}

'''

# Insert after the first server block (HTTP redirect for vectornode.ru)
insert_pos = cfg.find('server {\n    listen 443 ssl http2;\n    server_name vectornode.ru')
if insert_pos > 0:
    # Find the end of the HTTP redirect block
    http_block_end = cfg.find('}\n\nserver {\n    listen 443 ssl http2;\n    server_name vectornode.ru')
    if http_block_end > 0:
        insert_pos = http_block_end + 2  # After the closing brace and newlines
        cfg = cfg[:insert_pos] + '\n' + prepend + cfg[insert_pos:]

with sftp.open('/etc/nginx/sites-enabled/vectornode.ru', 'w') as f:
    f.write(cfg.encode())
sftp.close()

stdin, stdout, stderr = ssh.exec_command('nginx -t 2>&1')
print('Test:', stdout.read().decode(errors='replace').strip())

if 'successful' in (stdout.read().decode(errors='replace') + ''):
    print('Config ok')
else:
    stdin2, stdout2, stderr2 = ssh.exec_command('systemctl reload nginx 2>&1')
    print('Reload:', stdout2.read().decode(errors='replace').strip())

ssh.close()
