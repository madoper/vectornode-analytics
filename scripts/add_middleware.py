import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=10)

# Read current config
_, o, _ = ssh.exec_command('cat /opt/podft/infra/superset-init/superset_config.py')
config = o.read().decode(errors='replace')

# Add WSGI middleware before the fix_chart_patch import
middleware_code = '''
class FormDataInjectMiddleware:
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        from urllib.parse import parse_qs
        import json as _json
        if environ.get("PATH_INFO") == "/api/v1/chart/data" and environ.get("REQUEST_METHOD") == "POST":
            qs = environ.get("QUERY_STRING", "")
            params = parse_qs(qs)
            fd = params.get("form_data", [None])[0]
            if fd:
                try:
                    j = _json.loads(fd)
                    body = _json.dumps(j).encode()
                    environ["CONTENT_TYPE"] = "application/json"
                    environ["CONTENT_LENGTH"] = str(len(body))
                    environ["wsgi.input"] = __import__("io").BytesIO(body)
                except Exception:
                    pass
        return self.app(environ, start_response)

ADDITIONAL_MIDDLEWARE = [FormDataInjectMiddleware]
'''

# Insert before the fix_chart_patch import
if 'ADDITIONAL_MIDDLEWARE' not in config:
    # Find the right spot before the fix_chart_patch import
    old = '\n\nimport threading\nimport fix_chart_patch'
    new = middleware_code + '\n\nimport threading\nimport fix_chart_patch'
    if old in config:
        config = config.replace(old, new, 1)
        print('Middleware added before fix_chart_patch')
    else:
        # Try adding after the second ENABLE_PROXY_FIX
        old2 = "PROXY_FIX_CONFIG = "
        if old2 in config:
            idx = config.rfind(old2)
            # Find end of that line
            end_idx = config.find('\n', idx)
            insert_pos = config.find('\n', end_idx + 1)
            if insert_pos > 0:
                config = config[:insert_pos] + middleware_code + config[insert_pos:]
                print('Middleware added after PROXY_FIX_CONFIG')
            else:
                print('Could not find insert position')
else:
    print('Middleware already exists')

# Write back
sftp = ssh.open_sftp()
f = sftp.file('/opt/podft/infra/superset-init/superset_config.py', 'w')
f.write(config)
f.close()
sftp.close()

print('Config written')

# Verify
_, o2, _ = ssh.exec_command('grep ADDITIONAL_MIDDLEWARE /opt/podft/infra/superset-init/superset_config.py')
print('Verify:', o2.read().decode(errors='replace')[:200])

ssh.close()
