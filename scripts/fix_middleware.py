import paramiko, base64, time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

# Create a simple Python fix for the chart data API
# This module intercepts requests and copies form_data from URL query to request body
fix_code = '''
"""Fix for chart data POST endpoint - reads form_data from URL query params."""
import json
from flask import request

def before_request():
    if (request.method == "POST"
        and request.endpoint
        and "ChartDataRestApi" in request.endpoint
        and "form_data" in request.args
        and not request.is_json):
        try:
            fd = json.loads(request.args["form_data"])
            request._cached_json = (fd, fd)
        except Exception:
            pass
'''

sftp = ssh.open_sftp()
with sftp.open('/opt/podft/infra/superset-init/fix_chart_api.py', 'w') as f:
    f.write(fix_code.encode())
sftp.close()

# Copy to container
ssh.exec_command('docker cp /opt/podft/infra/superset-init/fix_chart_api.py podft-superset:/app/pythonpath/fix_chart_api.py')
print('Module copied')

# Update superset_config.py
stdin, stdout, stderr = ssh.exec_command('cat /opt/podft/infra/superset-init/superset_config.py')
cfg = stdout.read().decode()

# Remove previous patch attempts
for old in ['\nimport patch_form_data\n', '\nimport fix_chart_api\n',
            '\ntry:\n    patch_form_data.before_request\n']:
    cfg = cfg.replace(old, '')

# Remove the older block
cfg = cfg.replace(
    'from flask import request\ntry:\n    from superset.app import app as flask_app\n    flask_app.before_request(patch_form_data.before_request)\nexcept Exception:\n    pass\n',
    '')
cfg = cfg.replace(
    '''import flask\n    flask.current_app.before_request(patch_form_data.before_request)\nexcept Exception:\n    pass''',
    '')

# Add new import and hook
hook = '''
# Fix: read form_data from URL query params in chart data POST endpoint
import fix_chart_api
try:
    from flask import current_app
    current_app.before_request(fix_chart_api.before_request)
except Exception:
    pass
'''
cfg += hook

cfg_b64 = base64.b64encode(cfg.encode()).decode()
ssh.exec_command(f'echo {cfg_b64} | base64 -d > /opt/podft/infra/superset-init/superset_config.py')
print('Config updated')

# Remove the Nginx chart/data rewrite (no longer needed)
sftp2 = ssh.open_sftp()
with sftp2.open('/etc/nginx/sites-enabled/vectornode.ru', 'r') as f:
    nginx_cfg = f.read().decode('utf-8', errors='replace')

# Remove the chart/data location block
nginx_cfg = nginx_cfg.replace(
    "    # Fix: rewrite POST /api/v1/chart/data?form_data={slice_id:X} -> GET /api/v1/chart/X/data/\n    location /api/v1/chart/data {\n        if ($arg_form_data ~ \"slice_id[^0-9]*([0-9]+)\") {\n            set $slice_id $1;\n        }\n        proxy_method GET;\n        proxy_pass http://127.0.0.1:8088/api/v1/chart/$slice_id/data/$is_args$args;\n        proxy_set_header Host $host;\n        proxy_set_header X-Real-IP $remote_addr;\n        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;\n        proxy_set_header X-Forwarded-Proto $scheme;\n        proxy_set_header X-Forwarded-Host $host;\n    }\n",
    "")
nginx_cfg = nginx_cfg.replace('\nproxy_method', '\n# proxy_method')

with sftp2.open('/etc/nginx/sites-enabled/vectornode.ru', 'w') as f:
    f.write(nginx_cfg.encode('utf-8'))
sftp2.close()

stdin_ng, stdout_ng, stderr_ng = ssh.exec_command('nginx -t 2>&1 && systemctl reload nginx 2>&1')
print('Nginx:', stdout_ng.read().decode(errors='replace').strip()[:200])

# Restart Superset
ssh.exec_command('docker restart podft-superset')
print('Superset restarted')

time.sleep(25)

# Check status
stdin_st, stdout_st, stderr_st = ssh.exec_command('docker ps --filter name=superset --format "{{.Names}} {{.Status}}"')
print(stdout_st.read().decode(errors='replace').strip())

stdin_h, stdout_h, stderr_h = ssh.exec_command('curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8088/health')
print('Health:', stdout_h.read().decode(errors='replace').strip())

# Check logs for hook loading
stdin_l, stdout_l, stderr_l = ssh.exec_command('docker logs podft-superset --tail 5 2>&1')
print('Logs:', stdout_l.read().decode(errors='replace').strip()[:400])

ssh.close()
