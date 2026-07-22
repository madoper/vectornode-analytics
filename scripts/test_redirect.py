import paramiko, json, urllib.parse
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=10)

_, auth, _ = ssh.exec_command(
    'curl -s -X POST http://127.0.0.1:8088/api/v1/security/login -H "Content-Type: application/json" -d \'{"username":"admin","password":"admin","provider":"db"}\''
)
token = json.loads(auth.read().decode())["access_token"]

# Test redirect without -X POST (to first verify the redirect)
fd = urllib.parse.quote('{"slice_id":5}')
url = 'https://127.0.0.1/api/v1/chart/data?form_data=' + fd + '&dashboard_id=2'

# Just see the redirect status
_, o, _ = ssh.exec_command(
    'curl -s -k -w "REDIR_URL=%{redirect_url} HTTP_%{http_code}" -X POST "' + url + '" '
    '-H "Host: bi.vectornode.ru" '
    '-H "Authorization: Bearer ' + token + '"'
)
print('Redirect test (encoded):')
print(o.read().decode(errors='replace')[:300])

# Now follow redirect without -X POST (let curl auto-detect)
_, o2, _ = ssh.exec_command(
    'curl -s -k -L -w "\nHTTP_%{http_code}" "' + url + '" '
    '-H "Host: bi.vectornode.ru" '
    '-H "Authorization: Bearer ' + token + '"'
)
print('\n\nGET follow redirect:')
out = o2.read().decode(errors='replace')
print(out[:600])

ssh.close()
