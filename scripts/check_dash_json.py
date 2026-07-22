import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

# Check json_metadata
stdin, stdout, stderr = ssh.exec_command("docker exec podft-postgres psql -U podft -d superset -c \"SELECT json_metadata FROM dashboards WHERE id=2\" -A -t 2>&1")
meta = stdout.read().decode(errors='replace').strip()
print('json_metadata:')
print(meta[:500])

# Check position_json
stdin2, stdout2, stderr2 = ssh.exec_command("docker exec podft-postgres psql -U podft -d superset -c \"SELECT position_json FROM dashboards WHERE id=2\" -A -t 2>&1")
pos = stdout2.read().decode(errors='replace').strip()
print('\nposition_json:')
print(pos[:500])

ssh.close()
