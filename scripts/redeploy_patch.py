import paramiko, time
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=10)

# Write to host volume
VOLUME_PATH = '/var/lib/docker/volumes/podft_superset_data/_data'
with open(r'D:\project\FRS_TEST\scripts\fix_chart_patch.py', 'r') as src:
    content = src.read()

sftp = ssh.open_sftp()
f = sftp.file(f'{VOLUME_PATH}/fix_chart_patch.py', 'w')
f.write(content)
f.close()
sftp.close()

# Also remove fix_chart_api.py from volume (it may interfere)
_, o0, _ = ssh.exec_command(f'rm -f {VOLUME_PATH}/fix_chart_api.py 2>/dev/null; echo done')
print('Cleanup old file:', o0.read().decode(errors='replace'))

# Restart
_, o, _ = ssh.exec_command('docker restart podft-superset')
print('Restarting...')
time.sleep(20)

# Check logs
_, o2, _ = ssh.exec_command(
    'docker logs podft-superset 2>&1 | grep -i "patched\|Error\|Traceback" | tail -10'
)
print('\nLogs:')
print(o2.read().decode(errors='replace'))

# Test
import json, urllib.parse
time.sleep(5)
for attempt in range(2):
    _, auth, _ = ssh.exec_command(
        'curl -s -X POST http://127.0.0.1:8088/api/v1/security/login -H "Content-Type: application/json" -d \'{"username":"admin","password":"admin","provider":"db"}\''
    )
    resp = auth.read().decode(errors='replace')
    try:
        token = json.loads(resp)["access_token"]
        fd = urllib.parse.quote('{"slice_id":5}')
        _, o3, _ = ssh.exec_command(
            'curl -s -w "\nHTTP_%{http_code}" -X POST "http://127.0.0.1:8088/api/v1/chart/data?form_data=' + fd + '" '
            '-H "Authorization: Bearer ' + token + '"'
        )
        print('\nChart POST test (query only, no body):')
        print(o3.read().decode(errors='replace')[:500])
        break
    except:
        time.sleep(5)
else:
    print('Test failed')

ssh.close()
