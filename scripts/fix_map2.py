import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=10)
sftp = ssh.open_sftp()
with sftp.open('/etc/nginx/sites-enabled/vectornode.ru', 'r') as f:
    cfg = f.read().decode('utf-8', errors='replace')
# Direct replacement of the problematic line
old_line = '    "~\\"slice_id\\"[^0-9]*([0-9]+)" "$1";'
new_line = '    "~slice_id[^0-9]*([0-9]+)" "$1";'
cfg = cfg.replace(old_line, new_line)
with sftp.open('/etc/nginx/sites-enabled/vectornode.ru', 'w') as f:
    f.write(cfg.encode('utf-8'))
sftp.close()
ssh.exec_command('nginx -t 2>&1 && systemctl reload nginx 2>&1')
print('Done')
# Verify  
stdin, stdout, stderr = ssh.exec_command("grep slice_id /etc/nginx/sites-enabled/vectornode.ru | head -3")
print(stdout.read().decode(errors='replace').strip())
ssh.close()
