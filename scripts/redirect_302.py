import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=10)

sftp = ssh.open_sftp()
with sftp.open('/etc/nginx/sites-enabled/vectornode.ru', 'r') as f:
    cfg = f.read().decode('utf-8', errors='replace')

# Replace the entire location block with a simple redirect
old = '''location = /api/v1/chart/data {
        proxy_http_version 1.1;
        proxy_method GET;
        proxy_pass http://127.0.0.1:8088/api/v1/chart/$chart_slice_id/data/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $host;
    }'''

new = '''location = /api/v1/chart/data {
        return 302 /api/v1/chart/$chart_slice_id/data/;
    }'''

cfg = cfg.replace(old, new)

with sftp.open('/etc/nginx/sites-enabled/vectornode.ru', 'w') as f:
    f.write(cfg.encode('utf-8'))
sftp.close()

ssh.exec_command('nginx -t 2>&1 && systemctl reload nginx 2>&1')

# Test
import json
stdin, stdout, stderr = ssh.exec_command(
    "curl -s -X POST http://127.0.0.1:8088/api/v1/security/login "
    "-H 'Content-Type: application/json' "
    "-d '{\"username\":\"admin\",\"password\":\"admin\",\"provider\":\"db\"}'"
)
token = json.loads(stdout.read().decode())["access_token"]

# Test redirect with curl following
stdin2, stdout2, stderr2 = ssh.exec_command(
    'curl -s -L -o /dev/null -w "%{http_code}" -k -X POST "https://bi.vectornode.ru/api/v1/chart/data?form_data=%7B%22slice_id%22%3A1%7D" '
    '-H "Authorization: Bearer ' + token + '"'
)
print('Redirect test:', stdout2.read().decode(errors='replace').strip())

# Check what Location header says
stdin3, stdout3, stderr3 = ssh.exec_command(
    'curl -s -i -k -X POST "https://bi.vectornode.ru/api/v1/chart/data?form_data=%7B%22slice_id%22%3A1%7D" 2>&1 | head -15'
)
resp = stdout3.read().decode(errors='replace').strip()
for line in resp.split('\n')[:10]:
    if 'HTTP' in line or 'Location' in line:
        print(line[:200])

ssh.close()
