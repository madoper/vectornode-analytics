import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

cmds = [
    'sleep 5',
    'ss -tlnp | grep 8081',
    'journalctl -u airflow-webserver --no-pager -n 10 --output=short-precise 2>&1',
    'curl -s -o /dev/null -w "%{http_code}" http://localhost:8081/',
]

for cmd in cmds:
    print(f'> {cmd}')
    stdin, stdout, stderr = ssh.exec_command(cmd)
    print(stdout.read().decode(errors='replace').strip())
    err = stderr.read().decode(errors='replace').strip()
    if err:
        print('ERR:', err)

ssh.close()
