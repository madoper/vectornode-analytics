import paramiko, time, json, urllib.parse
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=10)

# 1. Deploy Nginx config (no redirect)
sftp = ssh.open_sftp()
sftp.put(r'D:\project\FRS_TEST\nginx\vectornode.conf', '/etc/nginx/sites-available/podft')
sftp.close()

_, o, _ = ssh.exec_command('nginx -t 2>&1')
print('nginx -t:', o.read().decode(errors='replace').strip())

_, o2, _ = ssh.exec_command('nginx -s reload 2>&1')
print('reload:', o2.read().decode(errors='replace').strip())

# 2. Deploy patch to volume
V = '/var/lib/docker/volumes/podft_superset_data/_data'
with open(r'D:\project\FRS_TEST\scripts\fix_chart_patch.py', 'r') as src:
    content = src.read()
sftp2 = ssh.open_sftp()
f = sftp2.file(f'{V}/fix_chart_patch.py', 'w')
f.write(content)
f.close()
sftp2.close()

ssh.exec_command(f'find {V} -name "*.pyc" -delete 2>/dev/null; find {V} -name "__pycache__" -exec rm -rf {{}} + 2>/dev/null')

# 3. Restart Superset
_, o3, _ = ssh.exec_command('docker restart podft-superset')
print('Superset restarting...')
time.sleep(25)

# 4. Check for hook message
_, o4, _ = ssh.exec_command('docker logs podft-superset --since 1m 2>&1 | grep -i "hook\|Traceback\|Error.*init" | head -5')
print('Recent logs:', o4.read().decode(errors='replace') or 'CLEAN')

# 5. Test
time.sleep(5)
_, auth, _ = ssh.exec_command(
    'curl -s -X POST http://127.0.0.1:8088/api/v1/security/login -H "Content-Type: application/json" -d \'{"username":"admin","password":"admin","provider":"db"}\''
)
resp = auth.read().decode(errors='replace')
token = json.loads(resp)["access_token"] if resp.startswith('{') else None
if not token:
    print('Login failed:', resp[:100])
    ssh.close()
    exit()

print('Login OK')

fd = urllib.parse.quote('{"slice_id":5}')
_, o5, _ = ssh.exec_command(
    'curl -s -w "\nHTTP_%{http_code}" -X POST "http://127.0.0.1:8088/api/v1/chart/data?form_data=' + fd + '" '
    '-H "Authorization: Bearer ' + token + '"'
)
print('\nChart POST (query only, no body):')
print(o5.read().decode(errors='replace')[:600])

ssh.close()
