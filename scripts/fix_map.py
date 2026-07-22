import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=10)

sftp = ssh.open_sftp()
with sftp.open('/etc/nginx/sites-enabled/vectornode.ru', 'r') as f:
    cfg = f.read().decode('utf-8', errors='replace')

# Fix: remove the quoted "slice_id" requirement, just match on `slice_id` text
old_map = 'map $arg_form_data $chart_slice_id {\n        "~\\"slice_id\\"[^0-9]*([0-9]+)" "$1";\n        default "";\n    }'
new_map = 'map $arg_form_data $chart_slice_id {\n        "~slice_id[^0-9]*([0-9]+)" "$1";\n        default "";\n    }'
cfg = cfg.replace(old_map, new_map)

# Restore the rewrite
old_debug = '        return 200 "sid=[$chart_slice_id] raw=[$arg_form_data]";'
new_rewrite = '        rewrite ^ /api/v1/chart/$chart_slice_id/data/ break;'
cfg = cfg.replace(old_debug, new_rewrite)

with sftp.open('/etc/nginx/sites-enabled/vectornode.ru', 'w') as f:
    f.write(cfg.encode('utf-8'))
sftp.close()

stdin, stdout, stderr = ssh.exec_command('nginx -t 2>&1 && systemctl reload nginx 2>&1')
print('Nginx:', stdout.read().decode(errors='replace').strip()[:200])

# Test
stdin2, stdout2, stderr2 = ssh.exec_command(
    'curl -s -k "https://bi.vectornode.ru/api/v1/chart/data?form_data=%7B%22slice_id%22%3A1%7D" 2>&1'
)
resp = stdin2[1].read().decode(errors='replace').strip()
print(f'Response: {resp[:200]}')

ssh.close()
