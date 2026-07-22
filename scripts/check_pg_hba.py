import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

cmds = [
    'docker exec podft-postgres sh -c "cat /var/lib/postgresql/data/pg_hba.conf"',
    'docker exec podft-postgres psql -U podft -c "SHOW password_encryption"',
    'docker exec podft-postgres psql -U podft -c "SHOW listen_addresses"',
]

for cmd in cmds:
    print('=== ' + cmd + ' ===')
    stdin, stdout, stderr = ssh.exec_command(cmd)
    print(stdout.read().decode().strip())
    err = stderr.read().decode().strip()
    if err:
        print('STDERR:', err)

ssh.close()
