import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

nginx_cfg = '''server {
    listen 80;
    server_name airflow.vectornode.ru;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name airflow.vectornode.ru;

    ssl_certificate /etc/letsencrypt/live/vectornode.ru/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/vectornode.ru/privkey.pem;

    location / {
        proxy_pass http://127.0.0.1:8081;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $host;
        proxy_connect_timeout 300s;
        proxy_read_timeout 300s;
        proxy_send_timeout 300s;
        client_max_body_size 50m;
    }
}
'''

sftp = ssh.open_sftp()
with sftp.open('/etc/nginx/sites-available/airflow', 'w') as f:
    f.write(nginx_cfg.encode())
sftp.close()

cmds = [
    'nginx -t 2>&1',
    'systemctl reload nginx 2>&1',
]

for cmd in cmds:
    stdin, stdout, stderr = ssh.exec_command(cmd)
    print(stdout.read().decode(errors='replace').strip())

ssh.close()
print('Nginx reloaded - airflow.vectornode.ru ready (SSL warning until DNS is configured)')
