import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=10)

# Check all columns with is_dttm = true for dataset 3
_, o, _ = ssh.exec_command(
    "docker exec podft-postgres psql -U podft -d superset -c "
    "\"SELECT column_name, type, is_dttm FROM table_columns WHERE table_id = 3 AND is_dttm = true\""
)
print('is_dttm=true columns:')
print(o.read().decode(errors='replace'))

ssh.close()
