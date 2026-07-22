import paramiko, base64, time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=10)

sftp = ssh.open_sftp()
with sftp.open('/etc/nginx/sites-enabled/vectornode.ru', 'r') as f:
    cfg = f.read().decode('utf-8', errors='replace')

# Replace the rewrite with a debug return
old = '        rewrite ^ /api/v1/chart/$chart_slice_id/data/ break;'
new = '        return 200 "sid=[$chart_slice_id] raw=[$arg_form_data]";'
cfg = cfg.replace(old, new)

with sftp.open('/etc/nginx/sites-enabled/vectornode.ru', 'w') as f:
    f.write(cfg.encode('utf-8'))
sftp.close()

stdin, stdout, stderr = ssh.exec_command('nginx -t 2>&1 && systemctl reload nginx 2>&1')
out = stdout.read().decode(errors='replace')
print('Nginx:', out[:200] if out else 'OK')

time.sleep(2)

# Test
stdin2, stdout2, stderr2 = ssh.exec_command(
    'curl -s -k "https://bi.vectornode.ru/api/v1/chart/data?form_data=%7B%22slice_id%22%3A1%7D" 2>&1'
)
print('Response:', stdout2.read().decode(errors='replace').strip()[:200])

ssh.close()
