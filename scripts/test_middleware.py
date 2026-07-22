import paramiko, json, urllib.parse, time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

time.sleep(25)

stdin, stdout, stderr = ssh.exec_command('curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8088/health')
health = stdout.read().decode(errors='replace').strip()
print(f'Health: {health}')

if health == '200':
    # Login
    std2 = ssh.exec_command(
        'curl -s -X POST http://127.0.0.1:8088/api/v1/security/login '
        '-H "Content-Type: application/json" '
        "-d '{\"username\":\"admin\",\"password\":\"admin\",\"provider\":\"db\"}'"
    )
    token = json.loads(std2[1].read().decode())["access_token"]
    print(f'Token: {token[:20]}...')

    # Test POST with form_data in URL (SPA format)
    fd = urllib.parse.quote(json.dumps({"slice_id": 1}))
    std3 = ssh.exec_command(
        f'curl -s -i -X POST "http://127.0.0.1:8088/api/v1/chart/data?form_data={fd}" '
        f'-H "Authorization: Bearer {token}" '
        f'-H "Content-Type: application/json" 2>&1 | head -25'
    )
    resp = std3[1].read().decode(errors='replace').strip()
    print(f'\nTest result:')
    status_line = resp.split('\n')[0] if '\n' in resp else resp[:100]
    print(status_line)
    # Find the body
    body_idx = resp.find('\n\n')
    if body_idx > 0:
        body = resp[body_idx+2:body_idx+300]
        print(f'Body: {body}')

    # Also test with empty POST body and form_data in URL
    std4 = ssh.exec_command(
        f'curl -s -i -X POST "http://127.0.0.1:8088/api/v1/chart/data?form_data={fd}" '
        f'-H "Authorization: Bearer {token}" 2>&1 | head -25'
    )
    resp4 = std4[1].read().decode(errors='replace').strip()
    print(f'\nNo Content-Type test:')
    status_line4 = resp4.split('\n')[0] if '\n' in resp4 else resp4[:100]
    print(status_line4)
    body_idx4 = resp4.find('\n\n')
    if body_idx4 > 0:
        body4 = resp4[body_idx4+2:body_idx4+300]
        print(f'Body: {body4}')
else:
    print('Superset not healthy yet')
    std_logs = ssh.exec_command('docker logs podft-superset --tail 15 2>&1')
    print(std_logs[1].read().decode(errors='replace').strip()[:800])

ssh.close()
