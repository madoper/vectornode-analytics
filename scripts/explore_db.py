import paramiko, json
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', port=22, username='root', password='8884&JKL%f75', timeout=10)

# Direct DB query - check filter_state table
cmds = [
    'docker exec podft-postgres psql -U podft -d superset -c "\\dt *filter*"',
    'docker exec podft-postgres psql -U podft -d superset -c "\\dt *key_value*"',
    'docker exec podft-postgres psql -U podft -d superset -c "SELECT * FROM key_value_entry LIMIT 1"',
]
for cmd in cmds:
    _, o, _ = ssh.exec_command(cmd)
    out = o.read().decode(errors='replace')
    if out.strip():
        print(out)
        print('---')

ssh.close()
