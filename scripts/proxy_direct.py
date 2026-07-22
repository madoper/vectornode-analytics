import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=10)

sftp = ssh.open_sftp()
with sftp.open('/etc/nginx/sites-enabled/vectornode.ru', 'r') as f:
    cfg = f.read().decode('utf-8', errors='replace')

# Replace rewrite+proxy_pass with direct proxy_pass using variable
old_block = 'location = /api/v1/chart/data {\n        rewrite ^ /api/v1/chart/$chart_slice_id/data/ break;\n        proxy_method GET;\n        proxy_pass http://127.0.0.1:8088;\n        proxy_set_header Host $host;\n        proxy_set_header X-Real-IP $remote_addr;\n        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;\n        proxy_set_header X-Forwarded-Proto $scheme;\n        proxy_set_header X-Forwarded-Host $host;\n    }'

new_block = 'location = /api/v1/chart/data {\n        proxy_method GET;\n        proxy_pass http://127.0.0.1:8088/api/v1/chart/$chart_slice_id/data/;\n        proxy_set_header Host $host;\n        proxy_set_header X-Real-IP $remote_addr;\n        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;\n        proxy_set_header X-Forwarded-Proto $scheme;\n        proxy_set_header X-Forwarded-Host $host;\n    }'

cfg = cfg.replace(old_block, new_block)

with sftp.open('/etc/nginx/sites-enabled/vectornode.ru', 'w') as f:
    f.write(cfg.encode('utf-8'))
sftp.close()

stdin, stdout, stderr = ssh.exec_command('nginx -t 2>&1 && systemctl reload nginx 2>&1')
out = stdout.read().decode(errors='replace')
print('Nginx:', out[:200] if out else 'OK')

# Test
import json
stdin2, stdout2, stderr2 = ssh.exec_command(
    "curl -s -X POST http://127.0.0.1:8088/api/v1/security/login "
    "-H 'Content-Type: application/json' "
    "-d '{\"username\":\"admin\",\"password\":\"admin\",\"provider\":\"db\"}'"
)
token = json.loads(stdout2.read().decode())["access_token"]

stdin3, stdout3, stderr3 = ssh.exec_command(
    'curl -s -k "https://bi.vectornode.ru/api/v1/chart/data?form_data=%7B%22slice_id%22%3A1%7D" '
    '-H "Authorization: Bearer ' + token + '" 2>&1 | head -c 400'
)
resp = stdout3.read().decode(errors='replace').strip()
print(f'Test: {resp[:300]}')

ssh.close()
