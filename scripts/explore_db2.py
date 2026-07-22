import paramiko, json
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', port=22, username='root', password='8884&JKL%f75', timeout=10)

cmds = [
    'docker exec podft-postgres psql -U podft -d superset -c "\\d key_value"',
    'docker exec podft-postgres psql -U podft -d superset -c "SELECT id, resource, LEFT(value::text, 300) FROM key_value ORDER BY id DESC LIMIT 5"',
]
for cmd in cmds:
    _, o, _ = ssh.exec_command(cmd)
    out = o.read().decode(errors='replace')
    if out.strip():
        print(out)
        print('---')

ssh.close()
