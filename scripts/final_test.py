import paramiko, json, time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

time.sleep(20)

stdin, stdout, stderr = ssh.exec_command('curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8088/health')
h = stdout.read().decode(errors='replace').strip()
print(f'Health: {h}')

if h == '200':
    std2 = ssh.exec_command(
        'curl -s -X POST http://127.0.0.1:8088/api/v1/security/login '
        '-H "Content-Type: application/json" '
        "-d '{\"username\":\"admin\",\"password\":\"admin\",\"provider\":\"db\"}'"
    )
    t = json.loads(std2[1].read().decode())["access_token"]
    fd = json.dumps({"slice_id": 1})
    std3 = ssh.exec_command(
        'curl -s -i -X POST "http://127.0.0.1:8088/api/v1/chart/data?form_data=' + fd + '" '
        '-H "Authorization: Bearer ' + t + '" 2>&1 | head -20'
    )
    all_lines = std3[1].read().decode(errors='replace').strip().split('\n')
    print(f'Status: {all_lines[0]}')
    for i, line in enumerate(all_lines):
        if line.startswith('{'):
            print(f'Response: {line[:300]}')
            break

ssh.close()
