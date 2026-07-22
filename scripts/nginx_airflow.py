import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

# First create a temporary HTTP-only config for airflow
nginx_cfg = '''server {
    listen 80;
    server_name airflow.vectornode.ru;

    location / {
        proxy_pass http://127.0.0.1:8081;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 300s;
        proxy_read_timeout 300s;
        proxy_send_timeout 300s;
    }
}
'''

sftp = ssh.open_sftp()
with sftp.open('/etc/nginx/sites-available/airflow', 'w') as f:
    f.write(nginx_cfg.encode())
sftp.close()

# Enable the site
cmds = [
    'ln -sf /etc/nginx/sites-available/airflow /etc/nginx/sites-enabled/airflow',
    'nginx -t 2>&1',
    'systemctl reload nginx 2>&1',
]

for cmd in cmds:
    print(f'> {cmd}')
    stdin, stdout, stderr = ssh.exec_command(cmd)
    print(stdout.read().decode(errors='replace').strip())

ssh.close()
