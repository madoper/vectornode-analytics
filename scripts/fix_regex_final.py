import paramiko, json

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=10)

sftp = ssh.open_sftp()
with sftp.open('/etc/nginx/sites-enabled/vectornode.ru', 'r') as f:
    cfg = f.read().decode('utf-8', errors='replace')

# Fix regex: match URL-encoded pattern %22%3A explicitly
old_line = '    "~slice_id[^0-9]*([0-9]+)" "$1";'
new_line = '    "~slice_id%22%3A([0-9]+)" "$1";'
cfg = cfg.replace(old_line, new_line)

with sftp.open('/etc/nginx/sites-enabled/vectornode.ru', 'w') as f:
    f.write(cfg.encode('utf-8'))
sftp.close()

ssh.exec_command('nginx -t 2>&1 && systemctl reload nginx 2>&1')

# Login
stdin, stdout, stderr = ssh.exec_command(
    "curl -s -X POST http://127.0.0.1:8088/api/v1/security/login "
    "-H 'Content-Type: application/json' "
    "-d '{\"username\":\"admin\",\"password\":\"admin\",\"provider\":\"db\"}'"
)
token = json.loads(stdout.read().decode())["access_token"]

# Check redirect Location
stdin2, stdout2, stderr2 = ssh.exec_command(
    'curl -s -i -k "https://bi.vectornode.ru/api/v1/chart/data?form_data=%7B%22slice_id%22%3A1%7D" 2>&1 | grep -i location'
)
print('Location:', stdout2.read().decode(errors='replace').strip()[:200])

# Test full redirect flow with auth
stdin3, stdout3, stderr3 = ssh.exec_command(
    'curl -s -L -o /dev/null -w "%{http_code}" -k "https://bi.vectornode.ru/api/v1/chart/data?form_data=%7B%22slice_id%22%3A1%7D" '
    '-H "Authorization: Bearer ' + token + '"'
)
print('Redirect flow:', stdout3.read().decode(errors='replace').strip())

# Verify direct GET still works
stdin4, stdout4, stderr4 = ssh.exec_command(
    'curl -s -o /dev/null -w "%{http_code}" -k "https://bi.vectornode.ru/api/v1/chart/1/data/" '
    '-H "Authorization: Bearer ' + token + '"'
)
print('Direct GET:', stdout4.read().decode(errors='replace').strip())

ssh.close()
