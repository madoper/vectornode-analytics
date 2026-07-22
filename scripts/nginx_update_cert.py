import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

sftp = ssh.open_sftp()
with sftp.open('/etc/nginx/sites-enabled/vectornode.ru', 'r') as f:
    cfg = f.read()

# Update SSL cert paths for subdomains
old = b'ssl_certificate /etc/letsencrypt/live/vectornode.ru/fullchain.pem;\n    ssl_certificate_key /etc/letsencrypt/live/vectornode.ru/privkey.pem;'

new = b'ssl_certificate /etc/letsencrypt/live/admin.vectornode.ru/fullchain.pem;\n    ssl_certificate_key /etc/letsencrypt/live/admin.vectornode.ru/privkey.pem;'

cfg = cfg.replace(old, new, 2)  # Replace first 2 occurrences (admin + bi blocks)

with sftp.open('/etc/nginx/sites-enabled/vectornode.ru', 'w') as f:
    f.write(cfg)

stdin, stdout, stderr = ssh.exec_command('nginx -t 2>&1 && systemctl reload nginx 2>&1')
print(stdout.read().decode(errors='replace').strip())

import time
time.sleep(2)

# Test
stdin2, stdout2, stderr2 = ssh.exec_command(
    "curl -s -o /dev/null -w '%{http_code}' https://bi.vectornode.ru/ 2>&1"
)
print(f'bi.vectornode.ru HTTPS: {stdout2.read().decode(errors="replace").strip()}')

stdin3, stdout3, stderr3 = ssh.exec_command(
    "curl -s -o /dev/null -w '%{http_code}' https://admin.vectornode.ru/ 2>&1"
)
print(f'admin.vectornode.ru HTTPS: {stdout3.read().decode(errors="replace").strip()}')

ssh.close()
