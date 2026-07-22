import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

sftp = ssh.open_sftp()
with sftp.open('/etc/nginx/sites-enabled/vectornode.ru', 'r') as f:
    cfg = f.read().decode('utf-8', errors='replace')

# Replace the /static/ location block to add the service-worker.js no-op
old = '''    # Direct proxy for Superset static assets (legacy path, needed for Service Worker + dynamic chunks)
    location /static/ {
        proxy_pass http://127.0.0.1:8088/static/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_buffering off;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }'''

new = '''    # No-op service worker to prevent 404 errors
    location = /static/service-worker.js {
        add_header Content-Type application/javascript;
        add_header Service-Worker-Allowed /;
        return 200 "self.addEventListener('install',()=>self.skipWaiting());self.addEventListener('activate',()=>self.clients.claim());";
    }

    # Direct proxy for Superset static assets (legacy path, needed for Service Worker + dynamic chunks)
    location /static/ {
        proxy_pass http://127.0.0.1:8088/static/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_buffering off;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }'''

cfg = cfg.replace(old, new)

with sftp.open('/etc/nginx/sites-enabled/vectornode.ru', 'w') as f:
    f.write(cfg.encode())
sftp.close()

stdin, stdout, stderr = ssh.exec_command('nginx -t 2>&1 && systemctl reload nginx 2>&1')
print(stdout.read().decode(errors='replace').strip())
ssh.close()
