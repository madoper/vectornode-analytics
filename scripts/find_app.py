import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=10)

# Find the app object in Superset
cmds = [
    'docker exec podft-superset python3 -c "import superset; print(dir(superset))" 2>&1',
    'docker exec podft-superset python3 -c "import superset.app; print(dir(superset.app))" 2>&1',
    'docker exec podft-superset python3 -c "from flask import current_app; print(type(current_app))" 2>&1',
]
for c in cmds:
    _, o, _ = ssh.exec_command(c)
    print(o.read().decode(errors='replace')[:500])
    print('---')

ssh.close()
