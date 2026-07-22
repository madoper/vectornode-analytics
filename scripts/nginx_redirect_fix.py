import paramiko, base64, time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

# Fix the config that crashed Superset - remove the broken import
stdin, stdout, stderr = ssh.exec_command('cat /opt/podft/infra/superset-init/superset_config.py')
cfg = stdout.read().decode()

# Remove the broken fix_chart_api import block
cfg = cfg.split('''
# Fix: read form_data from URL query params in chart data POST endpoint
import fix_chart_api
try:
    from flask import current_app
    current_app.before_request(fix_chart_api.before_request)
except Exception:
    pass''')[0]

cfg_b64 = base64.b64encode(cfg.encode()).decode()
ssh.exec_command(f'echo {cfg_b64} | base64 -d > /opt/podft/infra/superset-init/superset_config.py')
print('Config fixed')

# Restart Superset
ssh.exec_command('docker restart podft-superset')
print('Superset restarting...')
time.sleep(5)

# Now fix the Nginx to use a redirect approach
sftp = ssh.open_sftp()
with sftp.open('/etc/nginx/sites-enabled/vectornode.ru', 'r') as f:
    nginx = f.read().decode('utf-8', errors='replace')

# Remove any old chart/data blocks
nginx = nginx.replace(
    "    # Fix: rewrite POST /api/v1/chart/data?form_data={slice_id:X} -> GET /api/v1/chart/X/data/\n",
    ""
)
if 'location /api/v1/chart/data' in nginx:
    # Find and remove the block
    import re
    block_pattern = r'    # Fix: rewrite.*?\n    location /api/v1/chart/data \{.*?\n    }\n'
    nginx = re.sub(block_pattern, '', nginx, flags=re.DOTALL)

# Add new chart/data redirect location inside bi.vectornode.ru HTTPS block
redirect_block = '''    # Fix: redirect POST /api/v1/chart/data -> GET /api/v1/chart/{slice_id}/data/
    location /api/v1/chart/data {
        if ($arg_form_data ~ "slice_id[^0-9]*([0-9]+)") {
            set $chart_sid $1;
        }
        return 302 /api/v1/chart/$chart_sid/data/$is_args$args;
    }
'''

# Insert before the 'location /' in bi HTTPS block
old_loc = '    location = /static/service-worker.js {'
new_loc = redirect_block + '\n    location = /static/service-worker.js {'
nginx = nginx.replace(old_loc, new_loc)

with sftp.open('/etc/nginx/sites-enabled/vectornode.ru', 'w') as f:
    f.write(nginx.encode('utf-8'))
sftp.close()

stdin2, stdout2, stderr2 = ssh.exec_command('nginx -t 2>&1 && systemctl reload nginx 2>&1')
print('Nginx:', stdout2.read().decode(errors='replace').strip())

time.sleep(25)

# Check Superset health
stdin3, stdout3, stderr3 = ssh.exec_command('curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8088/health')
print('Health:', stdout3.read().decode(errors='replace').strip())

ssh.close()
