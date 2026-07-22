import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=10)

# Read and clean config
sftp = ssh.open_sftp()
with sftp.open('/etc/nginx/sites-enabled/vectornode.ru', 'r') as f:
    cfg = f.read().decode('utf-8', errors='replace')

# Remove ALL chart/data and $chart_sid references
lines = cfg.split('\n')
cleaned = []
skip_count = 0
for i, line in enumerate(lines):
    if 'location = /api/v1/chart/data' in line or 'location /api/v1/chart/data' in line:
        skip_count = 1
        continue
    if skip_count > 0:
        if line.strip() == '}':
            skip_count -= 1
        if 'if ($arg_form_data' in line or 'set $chart_sid' in line or 'return 302' in line:
            skip_count = max(skip_count, 1)
        continue
    if 'chart/data' in line and ('Fix' in line or 'Redirect' in line):
        continue
    if '$chart_sid' in line:
        continue
    cleaned.append(line)

cfg = '\n'.join(cleaned)

# Add map in http context (at the top of the file)
http_insert = 'http {\n'
proxy_map = '    map $arg_form_data $chart_slice_id {\n        "~\\\\"slice_id\\\\"[^0-9]*([0-9]+)" "$1";\n        default "";\n    }\n'
cfg = cfg.replace(http_insert, http_insert + proxy_map)

# Find the bi.vectornode.ru HTTPS server block
# and add a location that rewrites + proxies
# Insert after 'client_max_body_size 50m;'
bi_block_start = cfg.find('server_name bi.vectornode.ru;\n    ssl_certificate')
if bi_block_start > 0:
    # Find client_max_body_size in this block
    cms_start = cfg.find('client_max_body_size 50m;\n', bi_block_start)
    if cms_start > 0:
        insert_pos = cms_start + len('client_max_body_size 50m;\n')
        rewrite_block = '''    # Rewrite POST /api/v1/chart/data -> internal proxy to GET /api/v1/chart/{id}/data/
    location = /api/v1/chart/data {
        rewrite ^ /api/v1/chart/$chart_slice_id/data/ break;
        proxy_method GET;
        proxy_pass http://127.0.0.1:8088;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $host;
    }

'''
        cfg = cfg[:insert_pos] + rewrite_block + cfg[insert_pos:]

with sftp.open('/etc/nginx/sites-enabled/vectornode.ru', 'w') as f:
    f.write(cfg.encode('utf-8'))
sftp.close()

stdin, stdout, stderr = ssh.exec_command('nginx -t 2>&1')
print('Nginx:', stdout.read().decode(errors='replace').strip())

if 'successful' in str:
    ssh.exec_command('systemctl reload nginx')

ssh.close()
