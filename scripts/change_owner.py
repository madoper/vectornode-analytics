import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

# Change ownership of all analytics tables to dbt_user
cmds = [
    "docker exec podft-postgres psql -U podft -d analytics -c \"ALTER SCHEMA analytics OWNER TO dbt_user\"",
    "docker exec podft-postgres psql -U podft -d analytics -c \"ALTER SCHEMA staging OWNER TO dbt_user\"",
    "docker exec podft-postgres psql -U podft -d analytics -c \"GRANT dbt_user TO podft\"",
]

for cmd in cmds:
    stdin, stdout, stderr = ssh.exec_command(cmd)
    print(stdout.read().decode(errors='replace').strip()[:100])

ssh.close()
