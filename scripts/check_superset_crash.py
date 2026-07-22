import paramiko, time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

time.sleep(10)

cmds = [
    'docker ps --filter name=superset --format "{{.Names}} {{.Status}}"',
    'docker logs podft-superset --tail 30 2>&1',
    'curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8088/health 2>&1 || echo "curl failed"',
    'curl -s http://127.0.0.1:8088/health 2>&1',
    'curl -s http://127.0.0.1:8088/login/ -o /dev/null -w "%{http_code}" 2>&1',
]

for cmd in cmds:
    stdin, stdout, stderr = ssh.exec_command(cmd)
    res = stdout.read().decode(errors='replace').strip()
    err = stderr.read().decode(errors='replace').strip()
    print(f'>>> {cmd[:60]}')
    if res:
        print(res[:500])
    if err:
        print('ERR:', err[:200])

ssh.close()
