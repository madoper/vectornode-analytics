import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

cmds = [
    'docker exec podft-superset sh -c "python -c \"import psycopg2; c=psycopg2.connect(host=\\\\"postgres\\\", user=\\\\"podft\\\", password=\\\\"podft-secret\\\", dbname=\\\\"superset\\\"); print(c.get_dsn_parameters())\"" 2>&1',
    'docker exec podft-superset sh -c "getent hosts postgres" 2>&1',
    'docker exec podft-superset sh -c "ping -c 1 postgres -W 2" 2>&1 | head -3',
]

for cmd in cmds:
    print(f'> {cmd[:80]}')
    stdin, stdout, stderr = ssh.exec_command(cmd)
    print(stdout.read().decode(errors='replace').strip()[:300])
    err = stderr.read().decode(errors='replace').strip()
    if err:
        print('ERR:', err[:200])

ssh.close()
