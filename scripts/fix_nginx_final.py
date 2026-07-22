import paramiko, re

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

sftp = ssh.open_sftp()
with sftp.open('/etc/nginx/sites-enabled/vectornode.ru', 'r') as f:
    cfg = f.read().decode('utf-8', errors='replace')

# Remove ALL chart/data location blocks (duplicates)
block_pattern = r'\s*location /api/v1/chart/data \{.*?\n\s*\}'
cfg = re.sub(block_pattern, '', cfg, flags=re.DOTALL)

# Remove the comment lines too
cfg = re.sub(r'\s*# Fix: redirect POST.*?\n', '', cfg, flags=re.DOTALL)

# Find the bi.vectornode.ru HTTPS server block and add a CLEAN redirect
# The block we need to insert AFTER 'client_max_body_size 50m;' but BEFORE 'location = /static/'
insert_marker = '    location = /static/service-worker.js {'
new_block = '''    # Redirect POST /api/v1/chart/data to GET /api/v1/chart/{id}/data/
    location = /api/v1/chart/data {
        if ($arg_form_data ~ "slice_id[^0-9]*([0-9]+)") {
            set $chart_sid $1;
        }
        return 302 /api/v1/chart/$chart_sid/data/;
    }

''' + insert_marker

cfg = cfg.replace(insert_marker, new_block)

with sftp.open('/etc/nginx/sites-enabled/vectornode.ru', 'w') as f:
    f.write(cfg.encode('utf-8'))
sftp.close()

stdin, stdout, stderr = ssh.exec_command('nginx -t 2>&1 && systemctl reload nginx 2>&1')
print('Nginx:', stdout.read().decode(errors='replace').strip())

# Verify block exists
stdin2, stdout2, stderr2 = ssh.exec_command(
    "grep -A5 'chart/data' /etc/nginx/sites-enabled/vectornode.ru"
)
print('\nConfig:')
print(stdout2.read().decode(errors='replace').strip()[:500])

# Quick test
import json
stdin3, stdout3, stderr3 = ssh.exec_command(
    "curl -s -X POST http://127.0.0.1:8088/api/v1/security/login "
    "-H 'Content-Type: application/json' "
    "-d '{\"username\":\"admin\",\"password\":\"admin\",\"provider\":\"db\"}'"
)
token = json.loads(stdin3[1].read().decode())["access_token"]
fd = json.dumps({"slice_id": 1})
stdin4, stdout4, stderr4 = ssh.exec_command(
    'curl -s -i -L -X POST "https://bi.vectornode.ru/api/v1/chart/data?form_data=' + fd + '" '
    '-H "Authorization: Bearer ' + token + '" -k 2>&1 | head -15'
)
resp = stdin4[1].read().decode(errors='replace').strip()
print('\nTest redirect:')
for line in resp.split('\n')[:12]:
    if 'HTTP' in line or '200' in line or '404' in line:
        print(line[:150])
    elif line.startswith('{'):
        print('SUCCESS! Data received')
        break

ssh.close()
