import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

cmds = [
    # Superset uses its own DB - let's check which one
    'docker exec podft-postgres psql -U podft -d superset -c "\\dt" 2>/dev/null | head -20',
    # Check if superset DB exists and has tables
    'docker exec podft-postgres psql -U podft -c "\\c superset" 2>/dev/null; docker exec podft-postgres psql -U podft -d superset -c "SELECT table_name FROM information_schema.tables WHERE table_schema=\'public\'" 2>/dev/null',
]

for cmd in cmds:
    print(f'> {cmd[:80]}')
    stdin, stdout, stderr = ssh.exec_command(cmd)
    print(stdout.read().decode(errors='replace').strip()[:1000])

ssh.close()
