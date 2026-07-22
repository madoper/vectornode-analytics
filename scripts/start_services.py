import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

cmds = [
    'systemctl start airflow-webserver airflow-scheduler',
    'systemctl status airflow-webserver --no-pager -l 2>&1 | head -20',
    'systemctl status airflow-scheduler --no-pager -l 2>&1 | head -20',
]

for cmd in cmds:
    print(f'=== {cmd[:70]}... ===')
    stdin, stdout, stderr = ssh.exec_command(cmd)
    out = stdout.read().decode(errors='replace').strip()
    if out:
        print(out.encode('ascii', errors='replace').decode())
    err = stderr.read().decode(errors='replace').strip()
    if err:
        print('ERR:', err[:200].encode('ascii', errors='replace').decode())

ssh.close()
