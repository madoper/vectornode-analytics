import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', port=22, username='root', password='8884&JKL%f75', timeout=10)

# Get ALL key_value entries with their UUIDs
cmd = 'docker exec podft-postgres psql -U podft -d superset -c "SELECT id, uuid, resource, LEFT(encode(value, \'escape\'), 200) as val FROM key_value ORDER BY id DESC LIMIT 25"'
_, o, _ = ssh.exec_command(cmd)
print('All key_value entries:')
print(o.read().decode(errors='replace'))

ssh.close()
