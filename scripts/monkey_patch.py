import paramiko, base64, time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

# New approach: monkey-patch the ChartDataRestApi.data method directly
patch_code = '''
"""Fix chart data POST endpoint - read form_data from URL query params."""
import json

def _patch():
    from superset.charts.data.api import ChartDataRestApi
    _original_data = ChartDataRestApi.data

    def _patched_data(self, *args, **kwargs):
        from flask import request
        if request.args.get("form_data") and not request.is_json:
            try:
                fd = json.loads(request.args["form_data"])
                request._cached_json = (fd, fd)
                request.environ["CONTENT_TYPE"] = "application/json"
            except Exception:
                pass
        return _original_data(self, *args, **kwargs)

    ChartDataRestApi.data = _patched_data

_patch()
'''

sftp = ssh.open_sftp()
with sftp.open('/opt/podft/infra/superset-init/fix_chart_api.py', 'w') as f:
    f.write(patch_code.encode())
sftp.close()

ssh.exec_command('docker cp /opt/podft/infra/superset-init/fix_chart_api.py podft-superset:/app/pythonpath/fix_chart_api.py')
print('Module updated')

# Verify the config still imports fix_chart_api
stdin, stdout, stderr = ssh.exec_command('cat /opt/podft/infra/superset-init/superset_config.py | tail -10')
print('Config tail:', stdout.read().decode(errors='replace').strip()[:300])

# Restart Superset
ssh.exec_command('docker restart podft-superset')
print('Superset restarting...')

time.sleep(30)

# Test
stdin2, stdout2, stderr2 = ssh.exec_command('curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8088/health')
health = stdout2.read().decode(errors='replace').strip()
print(f'Health: {health}')

if health == '200':
    import json as j
    std3 = ssh.exec_command(
        "curl -s -X POST http://127.0.0.1:8088/api/v1/security/login "
        "-H 'Content-Type: application/json' "
        "-d '{\"username\":\"admin\",\"password\":\"admin\",\"provider\":\"db\"}'"
    )
    token = j.loads(std3[1].read().decode())["access_token"]
    fd = j.dumps({"slice_id": 1})
    std4 = ssh.exec_command(
        'curl -s -X POST "http://127.0.0.1:8088/api/v1/chart/data?form_data=' + fd + '" '
        '-H "Authorization: Bearer ' + token + '" 2>&1'
    )
    resp = std4[1].read().decode(errors='replace').strip()
    if resp.startswith('{') and 'result' in resp:
        print(f'SUCCESS! Response: {resp[:200]}')
    elif resp.startswith('{') and 'error' in resp:
        print(f'Error: {resp[:300]}')
    else:
        print(f'Response: {resp[:200]}')
else:
    std5 = ssh.exec_command('docker logs podft-superset --tail 10 2>&1')
    print(std5[1].read().decode(errors='replace').strip()[:500])

ssh.close()
