import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

sftp = ssh.open_sftp()
with sftp.open('/etc/nginx/sites-enabled/vectornode.ru', 'r') as f:
    cfg = f.read()

# Add rewrite rule for chart data POST to GET
# Insert in the bi.vectornode.ru HTTPS server block
old = b'    location / {\n        proxy_pass http://127.0.0.1:8088;\n        proxy_set_header Host $host;\n        proxy_set_header X-Real-IP $remote_addr;\n        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;\n        proxy_set_header X-Forwarded-Proto $scheme;\n        proxy_set_header X-Forwarded-Host $host;\n        proxy_connect_timeout 300s;\n        proxy_read_timeout 300s;\n        proxy_send_timeout 300s;\n    }'

new = b'''    # Fix: rewrite POST /api/v1/chart/data?form_data={slice_id:X} -> GET /api/v1/chart/X/data/
    location /api/v1/chart/data {
        if ($arg_form_data ~ "slice_id..: *([0-9]+)") {
            set $slice_id $1;
        }
        proxy_method GET;
        proxy_pass http://127.0.0.1:8088/api/v1/chart/$slice_id/data/$is_args$args;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $host;
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
    }'''

cfg = cfg.replace(old, new)

with sftp.open('/etc/nginx/sites-enabled/vectornode.ru', 'w') as f:
    f.write(cfg)

stdin, stdout, stderr = ssh.exec_command('nginx -t 2>&1 && systemctl reload nginx 2>&1')
print('Nginx:', stdout.read().decode(errors='replace').strip())

ssh.close()
