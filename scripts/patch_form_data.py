import paramiko, base64, time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

# Write the patch file that hooks into request processing
patch = '''import json, contextlib
from flask import request

def before_request():
    """Copy form_data from URL query params to request body for POST requests."""
    if request.method != "POST":
        return
    if not request.endpoint or not request.endpoint.endswith(".data"):
        return
    if request.is_json:
        return
    form_data = request.args.get("form_data")
    if not form_data:
        return
    with contextlib.suppress(Exception):
        request_json = json.loads(form_data)
        request._cached_json = (request_json, request_json)
'''

sftp = ssh.open_sftp()
with sftp.open('/opt/podft/infra/superset-init/patch_form_data.py', 'w') as f:
    f.write(patch.encode())
sftp.close()
print('Patch written')

# Copy to container
ssh.exec_command('docker cp /opt/podft/infra/superset-init/patch_form_data.py podft-superset:/app/pythonpath/patch_form_data.py 2>&1')
print('Copied to container')

# Get the config file
stdin, stdout, stderr = ssh.exec_command('cat /opt/podft/infra/superset-init/superset_config.py')
cfg = stdout.read().decode()

# Remove old patch if exists
cfg = cfg.replace(
    '\n# Patch for chart data API - reads form_data from URL query params\nimport patch_form_data\nfrom flask import request\ntry:\n    from superset.app import app as flask_app\n    flask_app.before_request(patch_form_data.before_request)\nexcept Exception:\n    pass\n',
    ''
)

# Add new patch
patch_import = '''
# Patch: read form_data from URL query params in chart data API
import patch_form_data
try:
    patch_form_data.before_request
    import flask
    flask.current_app.before_request(patch_form_data.before_request)
except Exception:
    pass
'''
cfg += patch_import

cfg_b64 = base64.b64encode(cfg.encode()).decode()
ssh.exec_command(f'echo {cfg_b64} | base64 -d > /opt/podft/infra/superset-init/superset_config.py')

print('Config updated')
ssh.exec_command('docker restart podft-superset')
print('Superset restarting...')

time.sleep(25)

# Check if healthy
stdin2, stdout2, stderr2 = ssh.exec_command('docker ps --filter name=superset --format "{{.Names}} {{.Status}}"')
print(stdout2.read().decode(errors='replace').strip())

stdin3, stdout3, stderr3 = ssh.exec_command('curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8088/health')
health = stdout3.read().decode(errors='replace').strip()
print(f'Health: {health}')

# Check logs for patch loading info
stdin4, stdout4, stderr4 = ssh.exec_command('docker logs podft-superset --tail 10 2>&1 | tail -5')
print('Logs:', stdout4.read().decode(errors='replace').strip()[:500])

ssh.close()
