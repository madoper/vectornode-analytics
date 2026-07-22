import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=10)
sftp = ssh.open_sftp()
with sftp.open('/etc/nginx/sites-enabled/vectornode.ru', 'r') as f:
    cfg = f.read().decode('utf-8', errors='replace')
old = 'return 200 "sid=[$chart_slice_id]";'
new = 'rewrite ^ /api/v1/chart/$chart_slice_id/data/ break;'
cfg = cfg.replace(old, new)
with sftp.open('/etc/nginx/sites-enabled/vectornode.ru', 'w') as f:
    f.write(cfg.encode('utf-8'))
sftp.close()
stdin, stdout, stderr = ssh.exec_command('nginx -t 2>&1 && systemctl reload nginx 2>&1')
print('Nginx:', stdout.read().decode(errors='replace').strip()[:100])
ssh.close()
