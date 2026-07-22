import paramiko, time
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=10)

V = '/var/lib/docker/volumes/podft_superset_data/_data'

# Write patch
with open(r'D:\project\FRS_TEST\scripts\fix_chart_patch.py', 'r') as src:
    content = src.read()
sftp = ssh.open_sftp()
f = sftp.file(f'{V}/fix_chart_patch.py', 'w')
f.write(content)
f.close()
sftp.close()

# Clean and restart
ssh.exec_command(f'find {V} -name "*.pyc" -delete 2>/dev/null; find {V} -name "__pycache__" -exec rm -rf {{}} + 2>/dev/null')

_, o, _ = ssh.exec_command('docker restart podft-superset')
print('Restarting...')
time.sleep(25)

# Check logs
_, o2, _ = ssh.exec_command('docker logs podft-superset 2>&1 | grep "hook\|Traceback\|NameError\|AttributeError" | tail -10')
print('Logs:', o2.read().decode(errors='replace') or 'CLEAN')

# Test
import json, urllib.parse
time.sleep(5)
_, auth, _ = ssh.exec_command(
    'curl -s -X POST http://127.0.0.1:8088/api/v1/security/login -H "Content-Type: application/json" -d \'{"username":"admin","password":"admin","provider":"db"}\''
)
token = json.loads(auth.read().decode(errors='replace'))["access_token"]

fd = urllib.parse.quote('{"slice_id":5}')
_, o3, _ = ssh.exec_command(
    'curl -s -w "\nHTTP_%{http_code}" -X POST "http://127.0.0.1:8088/api/v1/chart/data?form_data=' + fd + '" '
    '-H "Authorization: Bearer ' + token + '"'
)
print('\nChart POST (query only):')
print(o3.read().decode(errors='replace')[:500])

ssh.close()
