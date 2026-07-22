import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=10)
# Quick test: first put back debug return
sftp = ssh.open_sftp()
with sftp.open('/etc/nginx/sites-enabled/vectornode.ru', 'r') as f:
    cfg = f.read().decode('utf-8', errors='replace')
old_rw = 'rewrite ^ /api/v1/chart/$chart_slice_id/data/ break;'
new_rw = 'return 200 "sid=[$chart_slice_id]";'
cfg = cfg.replace(old_rw, new_rw)
with sftp.open('/etc/nginx/sites-enabled/vectornode.ru', 'w') as f:
    f.write(cfg.encode('utf-8'))
sftp.close()
ssh.exec_command('nginx -t 2>&1 && systemctl reload nginx 2>&1')
# Test
stdin, stdout, stderr = ssh.exec_command('curl -s -k "https://bi.vectornode.ru/api/v1/chart/data?form_data=%7B%22slice_id%22%3A1%7D" 2>&1')
resp = stdout.read().decode(errors='replace').strip()
print(resp[:200])
ssh.close()
