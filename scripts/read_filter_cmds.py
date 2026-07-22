import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', port=22, username='root', password='8884&JKL%f75', timeout=10)

# Read filter state create, update, get commands
cmds = [
    'docker exec podft-superset cat /app/superset/commands/dashboard/filter_state/create.py 2>/dev/null',
    'docker exec podft-superset cat /app/superset/commands/dashboard/filter_state/update.py 2>/dev/null',
]
for cmd in cmds:
    _, o, _ = ssh.exec_command(cmd)
    print(o.read().decode(errors='replace'))
    print('===END===')

ssh.close()
