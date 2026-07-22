import paramiko, base64, time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

# Upload the patch
sftp = ssh.open_sftp()
sftp.put(r'D:\project\FRS_TEST\scripts\fix_chart_patch.py', '/opt/podft/infra/superset-init/fix_chart_patch.py')
sftp.close()

ssh.exec_command('docker cp /opt/podft/infra/superset-init/fix_chart_patch.py podft-superset:/app/pythonpath/fix_chart_patch.py')
print('Patch uploaded')

# Update config to import and schedule patch
stdin, stdout, stderr = ssh.exec_command('cat /opt/podft/infra/superset-init/superset_config.py')
cfg = stdout.read().decode()

# Clean old imports  
for bad in ['import patch_form_data\n', 'import fix_chart_api\n',
            'CALL_INIT', 'fix_chart_api.before_request']:
    for line in cfg.split('\n'):
        if bad in line:
            cfg = cfg.replace(line + '\n', '')

# Add simple import + thread start
cfg += '''
import threading
import fix_chart_patch
threading.Thread(target=fix_chart_patch.init, daemon=True).start()
'''

cfg_b64 = base64.b64encode(cfg.encode()).decode()
ssh.exec_command(f'echo {cfg_b64} | base64 -d > /opt/podft/infra/superset-init/superset_config.py')
print('Config updated')

# Restart Superset
ssh.exec_command('docker restart podft-superset')
print('Restarting...')
time.sleep(35)

# Check health
stdin2, stdout2, stderr2 = ssh.exec_command('curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8088/health')
print('Health:', stdout2.read().decode(errors='replace').strip())

# Check logs
stdin3, stdout3, stderr3 = ssh.exec_command('docker logs podft-superset --tail 20 2>&1 | grep -i "patch\\|fix_chart\\|plugin" | head -5')
log = stdout3.read().decode(errors='replace').strip()
if log:
    print('Log:', log[:300])

# Test
import json
stdin4, stdout4, stderr4 = ssh.exec_command(
    "curl -s -X POST http://127.0.0.1:8088/api/v1/security/login "
    "-H 'Content-Type: application/json' "
    "-d '{\"username\":\"admin\",\"password\":\"admin\",\"provider\":\"db\"}'"
)
token = json.loads(stdout4.read().decode())["access_token"]

fd = json.dumps({"slice_id": 1})
stdin5, stdout5, stderr5 = ssh.exec_command(
    'curl -s -X POST "http://127.0.0.1:8088/api/v1/chart/data?form_data=' + fd + '" '
    '-H "Authorization: Bearer ' + token + '" 2>&1'
)
resp = stdout5.read().decode(errors='replace').strip()
print(f'\nDirect chart data test: {resp[:300]}')

ssh.close()
