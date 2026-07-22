import paramiko, json

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=10)

# Test with verbose via localhost
stdin, stdout, stderr = ssh.exec_command(
    'curl -s -v -X POST "http://127.0.0.1:80/api/v1/chart/data?form_data={%22slice_id%22:1}" '
    '-H "Host: bi.vectornode.ru" 2>&1 | head -30'
)
print('Direct test:')
print(stdout.read().decode(errors='replace').strip()[:800])

# Also test via HTTPS
stdin2, stdout2, stderr2 = ssh.exec_command(
    'curl -s -v -k -X POST "https://bi.vectornode.ru/api/v1/chart/data?form_data={%22slice_id%22:1}" '
    '2>&1 | grep -E "^>|<|HTTP|Location|404|200" | head -15'
)
print('\nHTTPS test:')
print(stdin2[1].read().decode(errors='replace').strip()[:500])

# Check if map is working
stdin3, stdout3, stderr3 = ssh.exec_command(
    "grep 'chart_slice_id' /etc/nginx/sites-enabled/vectornode.ru | head -5"
)
print('\nMap config:')
print(stdout3.read().decode(errors='replace').strip()[:300])

# Test the GET endpoint directly  
stdin4, stdout4, stderr4 = ssh.exec_command(
    "curl -s -X POST http://127.0.0.1:8088/api/v1/security/login "
    "-H 'Content-Type: application/json' "
    "-d '{\"username\":\"admin\",\"password\":\"admin\",\"provider\":\"db\"}'"
)
token = json.loads(stdin4[1].read().decode())["access_token"]

stdin5, stdout5, stderr5 = ssh.exec_command(
    "curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:8088/api/v1/chart/1/data/ "
    "-H 'Authorization: Bearer " + token + "'"
)
print(f'\nGET /chart/1/data/: {stdout5.read().decode(errors="replace").strip()}')

ssh.close()
