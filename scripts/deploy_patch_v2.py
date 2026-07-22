import paramiko, time
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=10)

# Upload fixed patch to host first
sftp = ssh.open_sftp()
f = sftp.file('/tmp/fix_chart_patch.py', 'w')
with open(r'D:\project\FRS_TEST\scripts\fix_chart_patch.py', 'r') as src:
    f.write(src.read())
f.close()
sftp.close()

# Copy into container volume
_, o, _ = ssh.exec_command('docker cp /tmp/fix_chart_patch.py podft-superset:/app/pythonpath/fix_chart_patch.py')
print('Copy:', o.read().decode(errors='replace'))

# Verify
_, o2, _ = ssh.exec_command('docker exec podft-superset cat /app/pythonpath/fix_chart_patch.py')
print('\nContainer fix_chart_patch.py:')
print(o2.read().decode(errors='replace'))

# Restart
_, o3, _ = ssh.exec_command('docker restart podft-superset')
print('\nRestarting...')

# Wait and check
time.sleep(15)
_, o4, _ = ssh.exec_command('docker logs podft-superset 2>&1 | grep -i "patched\|NameError\|_patch" | tail -5')
print('\nPatch logs:')
print(o4.read().decode(errors='replace'))

# Test chart POST
import json, urllib.parse
_, auth, _ = ssh.exec_command(
    'curl -s -X POST http://127.0.0.1:8088/api/v1/security/login -H "Content-Type: application/json" -d \'{"username":"admin","password":"admin","provider":"db"}\''
)
token = json.loads(auth.read().decode(errors='replace'))["access_token"]

fd = urllib.parse.quote('{"slice_id":5}')
_, o5, _ = ssh.exec_command(
    'curl -s -w "\nHTTP_%{http_code}" -X POST "http://127.0.0.1:8088/api/v1/chart/data?form_data=' + fd + '" '
    '-H "Authorization: Bearer ' + token + '"'
)
print('\n\nChart POST test (query only):')
print(o5.read().decode(errors='replace')[:400])

ssh.close()
