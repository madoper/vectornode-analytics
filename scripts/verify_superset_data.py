import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

cmds = [
    'docker exec podft-postgres psql -U podft -d superset -c "SELECT id, table_name, database_id, schema FROM tables"',
    'docker exec podft-postgres psql -U podft -d superset -c "SELECT id, dashboard_title, published FROM dashboards"',
]

for cmd in cmds:
    print(f'> {cmd[:70]}')
    stdin, stdout, stderr = ssh.exec_command(cmd)
    print(stdout.read().decode(errors='replace').strip())

ssh.close()
