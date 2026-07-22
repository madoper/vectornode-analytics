import paramiko, base64, time, json

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

# Read current config
stdin, stdout, stderr = ssh.exec_command('cat /opt/podft/infra/superset-init/superset_config.py')
cfg = stdout.read().decode()

# Remove old WTF_CSRF lines and add new config
cfg = cfg.replace('WTF_CSRF_ENABLED = True\n', 'WTF_CSRF_ENABLED = False\n')
cfg = cfg.replace('WTF_CSRF_EXEMPT_LIST = []\n', '')
cfg = cfg.replace('WTF_CSRF_EXEMPT_LIST = ["/api/v1/chart/data"]\n', '')

cfg_b64 = base64.b64encode(cfg.encode()).decode()
stdin2, stdout2, stderr2 = ssh.exec_command(
    f'echo {cfg_b64} | base64 -d > /opt/podft/infra/superset-init/superset_config.py && echo OK'
)
print('Write:', stdout2.read().decode(errors='replace').strip())

# Restart
ssh.exec_command('docker restart podft-superset')
time.sleep(20)

# Test
stdin3, stdout3, stderr3 = ssh.exec_command('curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8088/health')
print('Health:', stdout3.read().decode(errors='replace').strip())

# Test chart data
login = ssh.exec_command(
    'curl -s -X POST http://127.0.0.1:8088/api/v1/security/login '
    '-H "Content-Type: application/json" '
    '-d \'{"username":"admin","password":"admin","provider":"db"}\''
)
token = json.loads(login[1].read().decode())["access_token"]

payload = '{"form_data":"{\\"slice_id\\":1}","slice_id":1,"queries":[{"groupby":["criticality"],"metrics":[{"expressionType":"SIMPLE","aggregate":"COUNT","column":{"column_name":"company_id"},"label":"COUNT(company_id)"}]}]}'
query = ssh.exec_command(
    f'curl -s -X POST http://127.0.0.1:8088/api/v1/chart/data '
    f'-H "Authorization: Bearer {token}" '
    f'-H "Content-Type: application/json" '
    f'-d \'{payload}\' 2>&1'
)
result = query[1].read().decode(errors='replace').strip()
print(f'Chart data: {result[:400]}')

ssh.close()
