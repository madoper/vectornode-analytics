import paramiko, time
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=10)

# Clear all pycache
cmds = [
    'docker exec podft-superset find /app/pythonpath -name "*.pyc" -delete 2>&1; echo "pyc deleted"',
    'docker exec podft-superset find /app/pythonpath -name "__pycache__" -type d -exec rm -rf {} + 2>&1; echo "pycache dirs deleted"',
    'docker exec podft-superset find /app/pythonpath -name "*.pyc" 2>&1; echo "pyc remaining"',
]
for c in cmds:
    _, o, _ = ssh.exec_command(c)
    print(o.read().decode(errors='replace').strip())

# Restart
_, o2, _ = ssh.exec_command('docker restart podft-superset')
print('\nRestarting...')
time.sleep(15)

# Check logs
_, o3, _ = ssh.exec_command(
    'docker logs podft-superset 2>&1 | grep -i "patched\|_patch\|Error" | tail -10'
)
print('\nLogs:')
print(o3.read().decode(errors='replace'))

# Test chart POST
import json, urllib.parse
time.sleep(5)
_, auth, _ = ssh.exec_command(
    'curl -s -X POST http://127.0.0.1:8088/api/v1/security/login -H "Content-Type: application/json" -d \'{"username":"admin","password":"admin","provider":"db"}\''
)
resp = auth.read().decode(errors='replace')
try:
    token = json.loads(resp)["access_token"]
    fd = urllib.parse.quote('{"slice_id":5}')
    _, o4, _ = ssh.exec_command(
        'curl -s -w "\nHTTP_%{http_code}" -X POST "http://127.0.0.1:8088/api/v1/chart/data?form_data=' + fd + '" '
        '-H "Authorization: Bearer ' + token + '"'
    )
    print('\nChart POST test (query only):')
    print(o4.read().decode(errors='replace')[:400])
except:
    print('Test failed (Superset still starting?):', resp[:100])

ssh.close()
