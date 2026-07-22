import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

sftp = ssh.open_sftp()
with sftp.open('/etc/nginx/sites-enabled/vectornode.ru', 'r') as f:
    cfg = f.read()

# Fix login - match whitespace exactly
cfg = cfg.replace(b'''    location /login/ {
        proxy_pass http://127.0.0.1:8088/login/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        }''',
b'''    location /login/ {
        proxy_pass http://127.0.0.1:8088/login/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Prefix /superset;
        proxy_redirect / /superset/;
        }''')

# Fix logout
cfg = cfg.replace(b'''    location /logout/ {
        proxy_pass http://127.0.0.1:8088/logout/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        }''',
b'''    location /logout/ {
        proxy_pass http://127.0.0.1:8088/logout/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Prefix /superset;
        proxy_redirect / /superset/;
        }''')

# Fix user_info
cfg = cfg.replace(b'''    location /user_info/ {
        proxy_pass http://127.0.0.1:8088/user_info/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        }''',
b'''    location /user_info/ {
        proxy_pass http://127.0.0.1:8088/user_info/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Prefix /superset;
        proxy_redirect / /superset/;
        }''')

with sftp.open('/etc/nginx/sites-enabled/vectornode.ru', 'w') as f:
    f.write(cfg)

# Test
stdin, stdout, stderr = ssh.exec_command(b'nginx -t 2>&1 && systemctl reload nginx 2>&1')
print(stdout.read().decode(errors='replace').strip())

# Verify
stdin2, stdout2, stderr2 = ssh.exec_command(b"grep -A 13 'location /login/' /etc/nginx/sites-enabled/vectornode.ru")
print(stdout2.read().decode(errors='replace').strip())

ssh.close()
