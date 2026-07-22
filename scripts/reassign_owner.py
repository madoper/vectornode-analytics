import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

cmds = [
    'docker exec podft-postgres psql -U podft -d analytics -c "REASSIGN OWNED BY podft TO dbt_user"',
    'docker exec podft-postgres psql -U podft -d analytics -c "GRANT ALL ON ALL TABLES IN SCHEMA analytics TO dbt_user"',
    'docker exec podft-postgres psql -U podft -d analytics -c "GRANT ALL ON ALL SEQUENCES IN SCHEMA analytics TO dbt_user"',
    'docker exec podft-postgres psql -U podft -d analytics -c "GRANT ALL ON ALL TABLES IN SCHEMA staging TO dbt_user"',
]

for cmd in cmds:
    stdin, stdout, stderr = ssh.exec_command(cmd)
    print(stdout.read().decode(errors='replace').strip()[:200])

ssh.close()
