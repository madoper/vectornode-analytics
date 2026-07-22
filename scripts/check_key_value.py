import paramiko, json
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', port=22, username='root', password='8884&JKL%f75', timeout=10)

# Get the filter_state directly from the key_value table
# The resource column stores the filter state key
cmds = [
    'docker exec podft-postgres psql -U podft -d superset -c "SELECT id, resource, encode(value, \'escape\')::text FROM key_value WHERE resource NOT LIKE \'%%metastore%%\' ORDER BY id DESC LIMIT 10"',
    'docker exec podft-postgres psql -U podft -d superset -c "SELECT COUNT(*), resource FROM key_value GROUP BY resource"',
]
for cmd in cmds:
    _, o, _ = ssh.exec_command(cmd)
    out = o.read().decode(errors='replace')
    if out.strip():
        print(out)
        print('---')

ssh.close()
