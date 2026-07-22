import paramiko, time, json, urllib.parse
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', port=22, username='root', password='8884&JKL%f75', timeout=10)

# Login
_, auth, _ = ssh.exec_command(
    'curl -s -X POST http://127.0.0.1:8088/api/v1/security/login -H "Content-Type: application/json" -d \'{"username":"admin","password":"admin","provider":"db"}\''
)
token = json.loads(auth.read().decode(errors='replace'))["access_token"]

# Test with -L to follow the 302 redirect
fd = urllib.parse.quote('{"slice_id":5}')
_, co, _ = ssh.exec_command(
    'curl -s -L -w "\nHTTP_%{http_code}" -X POST "http://127.0.0.1:8088/api/v1/chart/data?form_data=' + fd + '" '
    '-H "Content-Type: application/json" '
    '-H "Authorization: Bearer ' + token + '"'
)
out = co.read().decode(errors='replace')
print('Chart POST (follow redirect):')
if 'HTTP_200' in out:
    print('   SUCCESS!')
    if '"query"' in out:
        idx = out.index('"query"')
        print('   ' + out[idx:idx+200])
    if '"error"' in out:
        ei = out.index('"error"')
        print('   error:', out[ei:ei+50])
elif 'HTTP_302' in out:
    print('   Got 302 (not followed)')
else:
    print('   ', out[:300])

# Also test GET directly to confirm it works
_, co2, _ = ssh.exec_command(
    'curl -s -w "\nHTTP_%{http_code}" "http://127.0.0.1:8088/api/v1/chart/5/data/" '
    '-H "Authorization: Bearer ' + token + '"'
)
print('\nGET chart/5/data/:', 'OK' if 'HTTP_200' in co2.read().decode(errors='replace') else 'FAIL')

ssh.close()
