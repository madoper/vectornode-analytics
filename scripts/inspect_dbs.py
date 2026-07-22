import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

cmds = [
    'docker exec podft-postgres psql -U podft -d superset -c "\\d dbs" 2>/dev/null',
    'docker exec podft-postgres psql -U podft -d superset -c "SELECT id, database_name, sqlalchemy_uri FROM dbs" 2>/dev/null',
]

for cmd in cmds:
    print(f'> {cmd[:80]}')
    stdin, stdout, stderr = ssh.exec_command(cmd)
    print(stdout.read().decode(errors='replace').strip()[:1500])

ssh.close()
