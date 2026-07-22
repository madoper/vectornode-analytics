import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=10)

# Read entire config
sftp = ssh.open_sftp()
with sftp.open('/etc/nginx/sites-enabled/vectornode.ru', 'r') as f:
    cfg = f.read().decode('utf-8', errors='replace')

# Find all lines with chart/data or chart_sid and remove those blocks
lines = cfg.split('\n')
cleaned = []
skip = False
for i, line in enumerate(lines):
    if 'location = /api/v1/chart/data' in line or 'location /api/v1/chart/data' in line:
        skip = True
        continue
    if skip:
        if line.strip() == '}':
            skip = False
        continue
    if '# Redirect POST /api/v1/chart/data' in line or '# Fix: redirect' in line:
        continue
    cleaned.append(line)

cfg = '\n'.join(cleaned)

# Now insert the redirect block in the correct place
# Find 'location = /static/service-worker.js' in the bi HTTPS block
insert_target = '    location = /static/service-worker.js {'
redirect = '''    # Redirect POST /api/v1/chart/data -> GET /api/v1/chart/{id}/data/
    location = /api/v1/chart/data {
        internal;
    }
'''
# Wait, this doesn't work for redirecting. Let me use a rewrite instead.

# Actually, let me use a different approach: rewrite at the server level
# Find the bi HTTPS server block and add rewrite before it
marker = '    location = /static/service-worker.js {'
new_block = '''    # Redirect POST /api/v1/chart/data?form_data={slice_id:X} -> GET /api/v1/chart/X/data/
    location = /api/v1/chart/data {
        if ($arg_form_data ~ "slice_id[^0-9]*([0-9]+)") {
            set $chart_sid $1;
        }
        return 302 /api/v1/chart/$chart_sid/data/;
    }

    location = /static/service-worker.js {'''

cfg = cfg.replace(marker, new_block)

with sftp.open('/etc/nginx/sites-enabled/vectornode.ru', 'w') as f:
    f.write(cfg.encode('utf-8'))
sftp.close()

stdin, stdout, stderr = ssh.exec_command('nginx -t 2>&1')
err_output = stderr.read().decode(errors='replace')
std_output = stdout.read().decode(errors='replace')
print(std_output)
if err_output:
    print('STDERR:', err_output[:300])

ssh.close()
