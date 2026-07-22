import paramiko, json

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

# Test Nginx map by sending request with empty chart_slice_id and checking
stdin, stdout, stderr = ssh.exec_command(
    "curl -s -X POST http://127.0.0.1/api/v1/chart/data "
    "-H 'Host: bi.vectornode.ru' "
    "-H 'X-Debug-SID: test' 2>&1 | grep -i '404\\|200\\|error' | head -5"
)
print('Test 1:', stdout.read().decode(errors='replace').strip()[:200])

# Login and test via Nginx with auth
stdin2, stdout2, stderr2 = ssh.exec_command(
    "curl -s -X POST http://127.0.0.1:8088/api/v1/security/login "
    "-H 'Content-Type: application/json' "
    "-d '{\"username\":\"admin\",\"password\":\"admin\",\"provider\":\"db\"}'"
)
token = json.loads(stdout2.read().decode())["access_token"]

# Test with proper form_data
fd = '{"slice_id":1}'
stdin3, stdout3, stderr3 = ssh.exec_command(
    f'curl -s -v "http://127.0.0.1/api/v1/chart/data?form_data={fd}" '
    f'-H "Host: bi.vectornode.ru" '
    f'-H "Authorization: Bearer {token}" 2>&1 | grep -E "HTTP|Location|404|200" | head -5'
)
print('Test 2:', stdout3.read().decode(errors='replace').strip()[:300])

# Test with URL-encoded
import urllib.parse
fd2 = urllib.parse.quote('{"slice_id":1}')
stdin4, stdout4, stderr4 = ssh.exec_command(
    f'curl -s -v "http://127.0.0.1/api/v1/chart/data?form_data={fd2}" '
    f'-H "Host: bi.vectornode.ru" '
    f'-H "Authorization: Bearer {token}" 2>&1 | grep -E "HTTP|Location|404|200" | head -5'
)
print('Test 3:', stdout4.read().decode(errors='replace').strip()[:300])

# Direct test of GET endpoint
stdin5, stdout5, stderr5 = ssh.exec_command(
    "curl -s -o /dev/null -w '%{http_code}' 'http://127.0.0.1:8088/api/v1/chart/1/data/' "
    f"-H 'Authorization: Bearer {token}'"
)
print('GET endpoint:', stdout5.read().decode(errors='replace').strip())

# Test what Superset returns for POST 
stdin6, stdout6, stderr6 = ssh.exec_command(
    f'curl -s -o /dev/null -w "%{{http_code}}" -X POST "http://127.0.0.1:8088/api/v1/chart/data?form_data={fd2}" '
    f'-H "Authorization: Bearer {token}"'
)
print('Direct POST to Superset:', stdout6.read().decode(errors='replace').strip())

ssh.close()
