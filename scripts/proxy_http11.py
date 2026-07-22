import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=10)

sftp = ssh.open_sftp()
with sftp.open('/etc/nginx/sites-enabled/vectornode.ru', 'r') as f:
    cfg = f.read().decode('utf-8', errors='replace')

oid = 'location = /api/v1/chart/data {\n        proxy_method GET;\n        proxy_pass'
nid = 'location = /api/v1/chart/data {\n        proxy_http_version 1.1;\n        proxy_method GET;\n        proxy_pass'
cfg = cfg.replace(oid, nid)

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

stdin2, stdout2, stderr2 = ssh.exec_command(
    'curl -s -o /dev/null -w "%{http_code}" -k -X POST "https://bi.vectornode.ru/api/v1/chart/data?form_data=%7B%22slice_id%22%3A1%7D" '
    '-H "Authorization: Bearer ' + token + '"'
)
print('Result:', stdout2.read().decode(errors='replace').strip())

# If still 404, test direct proxy via localhost
stdin3, stdout3, stderr3 = ssh.exec_command(
    'curl -s -o /dev/null -w "%{http_code}" -X POST "http://127.0.0.1/api/v1/chart/data?form_data=%7B%22slice_id%22%3A1%7D" '
    '-H "Host: bi.vectornode.ru" -H "Authorization: Bearer ' + token + '"'
)
print('Local HTTP:', stdout3.read().decode(errors='replace').strip())

ssh.close()
