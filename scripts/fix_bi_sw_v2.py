import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

sftp = ssh.open_sftp()
with sftp.open('/etc/nginx/sites-enabled/vectornode.ru', 'r') as f:
    cfg = f.read()

sw_js = "self.addEventListener('install',()=>self.skipWaiting());self.addEventListener('activate',()=>self.clients.claim());"
sw_block = (
    b'\n    location = /static/service-worker.js {\n'
    b'        add_header Content-Type application/javascript;\n'
    b'        add_header Service-Worker-Allowed /;\n'
    b'        return 200 "' + sw_js.encode() + b'";\n'
    b'    }\n'
)

old = b'    location / {\n        proxy_pass http://127.0.0.1:8088;\n        proxy_set_header Host $host;'
new = sw_block + old

cfg = cfg.replace(old, new, 1)

with sftp.open('/etc/nginx/sites-enabled/vectornode.ru', 'w') as f:
    f.write(cfg)
sftp.close()

stdin, stdout, stderr = ssh.exec_command('nginx -t 2>&1 && systemctl reload nginx 2>&1')
print(stdout.read().decode(errors='replace').strip())

import time
time.sleep(2)
stdin2, stdout2, stderr2 = ssh.exec_command('curl -s -o /dev/null -w "%{http_code}" https://bi.vectornode.ru/static/service-worker.js 2>&1')
print('SW:', stdout2.read().decode(errors='replace').strip())

ssh.close()
