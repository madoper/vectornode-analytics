import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

# Check admin password in Superset
cmds = [
    'docker exec podft-superset sh -c "cat /app/superset/superset/__init__.py 2>/dev/null | head -5"',
    'docker exec podft-superset sh -c "ls /app/superset/bin/ 2>/dev/null"',
    'docker exec podft-postgres psql -U podft -d superset -c "SELECT id, username, password, email FROM ab_user"',
]

for cmd in cmds:
    print(f'> {cmd[:70]}')
    stdin, stdout, stderr = ssh.exec_command(cmd)
    print(stdout.read().decode(errors='replace').strip()[:500])

ssh.close()
