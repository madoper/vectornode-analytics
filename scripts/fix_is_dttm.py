import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=10)

# Fix is_dttm for year column
_, o, _ = ssh.exec_command(
    "docker exec podft-postgres psql -U podft -d superset -c \"UPDATE table_columns SET is_dttm = false WHERE id = 10\""
)
print(o.read().decode(errors='replace'))

# Verify
_, o2, _ = ssh.exec_command(
    "docker exec podft-postgres psql -U podft -d superset -c \"SELECT id, column_name, is_dttm, type FROM table_columns WHERE id = 10\""
)
print(o2.read().decode(errors='replace'))

ssh.close()
