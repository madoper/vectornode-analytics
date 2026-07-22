import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=10)

cmds = [
    'docker exec podft-postgres psql -U podft -d analytics -c "SELECT schemaname, viewname FROM pg_views WHERE viewname LIKE \'v_%\'" 2>&1',
    'docker exec podft-postgres psql -U podft -d analytics -c "SHOW search_path" 2>&1',
    'docker exec podft-postgres psql -U podft -d analytics -c "\dn" 2>&1',
]
for c in cmds:
    _, stdout, _ = ssh.exec_command(c)
    print(stdout.read().decode(errors='replace'))
    print('---')
ssh.close()
