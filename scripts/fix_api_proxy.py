import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

sftp = ssh.open_sftp()
with sftp.open('/etc/nginx/sites-enabled/vectornode.ru', 'r') as f:
    cfg = f.read().decode('utf-8', errors='replace')

old = '''    location /api/ {
        proxy_pass http://gateway;'''

new = '''    location /api/v1/ {
        proxy_pass http://127.0.0.1:8088/api/v1/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Prefix /superset;
        proxy_redirect / /superset/;
    }

    location /api/ {
        proxy_pass http://gateway;'''

cfg = cfg.replace(old, new)

with sftp.open('/etc/nginx/sites-enabled/vectornode.ru', 'w') as f:
    f.write(cfg.encode())
sftp.close()

stdin, stdout, stderr = ssh.exec_command('nginx -t 2>&1 && systemctl reload nginx 2>&1')
print('Nginx:', stdout.read().decode(errors='replace').strip())

# Test
stdin2, stdout2, stderr2 = ssh.exec_command(
    'curl -s -o /dev/null -w "%{http_code}" https://vectornode.ru/api/v1/database/'
)
print(f'/api/v1/database/: {stdout2.read().decode(errors="replace").strip()}')

stdin3, stdout3, stderr3 = ssh.exec_command(
    'curl -s -o /dev/null -w "%{http_code}" https://vectornode.ru/api/health'
)
print(f'/api/health (gateway): {stdout3.read().decode(errors="replace").strip()}')

ssh.close()
