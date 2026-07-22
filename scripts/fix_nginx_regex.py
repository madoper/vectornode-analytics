import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

sftp = ssh.open_sftp()
with sftp.open('/etc/nginx/sites-enabled/vectornode.ru', 'r') as f:
    cfg = f.read().decode('utf-8', errors='replace')

# Fix the regex pattern
old_regex = 'if ($arg_form_data ~ "slice_id..: *([0-9]+)")'
new_regex = 'if ($arg_form_data ~ "slice_id[^0-9]*([0-9]+)")'
cfg = cfg.replace(old_regex, new_regex)

with sftp.open('/etc/nginx/sites-enabled/vectornode.ru', 'w') as f:
    f.write(cfg.encode('utf-8'))

stdin, stdout, stderr = ssh.exec_command('nginx -t 2>&1 && systemctl reload nginx 2>&1')
print('Nginx:', stdout.read().decode(errors='replace').strip())

# Test via curl
import json, urllib.parse
stdin2, stdout2, stderr2 = ssh.exec_command(
    'curl -s -X POST http://127.0.0.1:8088/api/v1/security/login '
    '-H "Content-Type: application/json" '
    '-d \'{"username":"admin","password":"admin","provider":"db"}\''
)
token = json.loads(stdout2.read().decode())["access_token"]

# Test via Nginx redirect (POST with form_data in URL)
fd = urllib.parse.quote(json.dumps({"slice_id": 1}))
# Test via HTTPS Nginx (direct to bi.vectornode.ru HTTPS block)
result_cmd = f'curl -s -i -X POST "https://bi.vectornode.ru/api/v1/chart/data?form_data={fd}" -H "Authorization: Bearer {token}" -k 2>&1 | head -25'
stdin3, stdout3, stderr3 = ssh.exec_command(result_cmd)
print('\nTest result:')
print(stdout3.read().decode(errors='replace').strip()[:500])

ssh.close()
