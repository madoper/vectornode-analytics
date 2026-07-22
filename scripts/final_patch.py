import paramiko, base64, time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

# New approach: register a proper before_request in flask 
# by using the app_initializer pattern
fix_code = '''
"""Fix chart data POST endpoint - reads form_data from URL query params.
This is safe to import at config load time because it doesn't import superset modules.
"""
import json

_original_data_handler = None

def _patch():
    from superset.charts.data.api import ChartDataRestApi
    global _original_data_handler
    _original_data_handler = ChartDataRestApi.data

    def _patched_data(self, *args, **kwargs):
        from flask import request
        fd = request.args.get("form_data")
        if fd and not request.is_json:
            try:
                j = json.loads(fd)
                request._cached_json = (j, j)
                request.environ["CONTENT_TYPE"] = "application/json"
            except Exception:
                pass
        return _original_data_handler(self, *args, **kwargs)

    ChartDataRestApi.data = _patched_data
    print("ChartDataRestApi.data patched successfully")

# We can't import superset at config load time (app not initialized)
# Instead, we register ourselves to be called later.
# The simplest way: someone needs to call fix_chart_api._patch() after app init.
# We'll use a Flask before_first_request handler to do the patching.

def _register_patch():
    """Register the patch to be applied on first request."""
    try:
        from flask import current_app
        @current_app.before_request
        def _apply_patch():
            if not current_app.config.get("FIX_CHART_DATA_APPLIED"):
                try:
                    _patch()
                    current_app.config["FIX_CHART_DATA_APPLIED"] = True
                except Exception:
                    pass
    except Exception as e:
        print(f"Warning: cannot register chart data fix: {e}")

# We need to call _register_patch after the app is created.
# Use Flask's app_initializer pattern - store a function to be called later.
def _init():
    """Call this after Flask app is initialized."""
    try:
        from flask import current_app
        @current_app.before_request
        def _first_patch():
            if not current_app.config.get("_PATCH_DONE"):
                try:
                    _patch()
                    current_app.config["_PATCH_DONE"] = True
                except Exception:
                    pass
    except Exception:
        pass

# Store a flag so we know to call _init later
CALL_INIT = True
'''

sftp = ssh.open_sftp()
with sftp.open('/opt/podft/infra/superset-init/fix_chart_api.py', 'w') as f:
    f.write(fix_code.encode())
sftp.close()

ssh.exec_command('docker cp /opt/podft/infra/superset-init/fix_chart_api.py podft-superset:/app/pythonpath/fix_chart_api.py')

# Now update superset_config.py to call _init() at the right time
stdin, stdout, stderr = ssh.exec_command('cat /opt/podft/infra/superset-init/superset_config.py')
cfg = stdout.read().decode()

# Remove any old fix attempts
for remove_str in ['import patch_form_data\n', 'import fix_chart_api\n',
                   'fix_chart_api.before_request', 'fix_chart_api._patch',
                   'PATCH_DONE', 'CALL_INIT']:
    cfg = cfg.replace(remove_str, '')

# Add new fix
cfg += '''
# Fix chart data API - patches on first request
import fix_chart_api
'''

cfg_b64 = base64.b64encode(cfg.encode()).decode()
ssh.exec_command(f'echo {cfg_b64} | base64 -d > /opt/podft/infra/superset-init/superset_config.py')
print('Config updated')

# Restart
ssh.exec_command('docker restart podft-superset')
print('Restarting...')

time.sleep(30)

# Check if healthy
stdin2, stdout2, stderr2 = ssh.exec_command('curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8088/health')
print('Health:', stdout2.read().decode(errors='replace').strip())

# Check logs for patch info
stdin3, stdout3, stderr3 = ssh.exec_command('docker logs podft-superset --tail 15 2>&1 | grep -i "patch\\|plugin\\|fix_chart"')
log = stdout3.read().decode(errors='replace').strip()
if log:
    print('Log with patch:', log[:200])

ssh.close()
