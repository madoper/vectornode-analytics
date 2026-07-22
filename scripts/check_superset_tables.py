import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

cmds = [
    'docker exec podft-postgres psql -U podft -d superset -c "\\d tables"',
    'docker exec podft-postgres psql -U podft -d superset -c "\\d slices"',
    'docker exec podft-postgres psql -U podft -d superset -c "\\d dashboards"',
    'docker exec podft-postgres psql -U podft -d superset -c "\\d dashboard_slices"',
]

for cmd in cmds:
    print(f'> {cmd[:70]}')
    stdin, stdout, stderr = ssh.exec_command(cmd)
    print(stdout.read().decode(errors='replace').strip()[:1000])

ssh.close()
