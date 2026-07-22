import paramiko, base64, time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

# Fixed version of the middleware
fix_code = '''
"""Fix for chart data POST endpoint - reads form_data from URL query params."""
import json
from io import BytesIO
from urllib.parse import quote
from flask import request

def before_request():
    if (request.method == "POST"
        and request.endpoint
        and "ChartDataRestApi" in request.endpoint
        and "form_data" in request.args
        and not request.is_json
        and not request.form.get("form_data")):
        try:
            fd = request.args["form_data"]
            body = ("form_data=" + quote(fd)).encode()
            request.environ["wsgi.input"] = BytesIO(body)
            request.environ["CONTENT_LENGTH"] = str(len(body))
            request.environ["CONTENT_TYPE"] = "application/x-www-form-urlencoded"
        except Exception:
            pass
'''

sftp = ssh.open_sftp()
with sftp.open('/opt/podft/infra/superset-init/fix_chart_api.py', 'w') as f:
    f.write(fix_code.encode())
sftp.close()

ssh.exec_command('docker cp /opt/podft/infra/superset-init/fix_chart_api.py podft-superset:/app/pythonpath/fix_chart_api.py')
print('Module updated')

# Restart Superset
ssh.exec_command('docker restart podft-superset')
print('Superset restarting...')

time.sleep(30)

# Check and test
stdin, stdout, stderr = ssh.exec_command('curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8088/health')
health = stdout.read().decode(errors='replace').strip()
print(f'Health: {health}')

if health == '200':
    import json as j
    std2 = ssh.exec_command(
        'curl -s -X POST http://127.0.0.1:8088/api/v1/security/login '
        '-H "Content-Type: application/json" '
        "-d '{\"username\":\"admin\",\"password\":\"admin\",\"provider\":\"db\"}'"
    )
    token = j.loads(std2[1].read().decode())["access_token"]
    
    # Test POST with form_data only in URL query (SPA format)
    fd_val = j.dumps({"slice_id": 1})
    std3 = ssh.exec_command(
        'curl -s -i -X POST "http://127.0.0.1:8088/api/v1/chart/data?form_data=' + fd_val + '" '
        '-H "Authorization: Bearer ' + token + '" 2>&1 | head -25'
    )
    resp = std3[1].read().decode(errors='replace').strip()
    print(f'\nTest:')
    lines = resp.split('\n')
    print(lines[0] if lines else resp[:100])
    body_start = resp.find('\n\n')
    if body_start > 0:
        print('Body:', resp[body_start:body_start+200])
else:
    std_l = ssh.exec_command('docker logs podft-superset --tail 8 2>&1')
    print('Logs:', std_l[1].read().decode(errors='replace').strip()[:500])

ssh.close()
