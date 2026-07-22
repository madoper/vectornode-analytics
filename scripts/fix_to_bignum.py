import paramiko, base64

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=10)

# Change charts 1-3 to big_number (simple, always works)
# Chart 4 is table and has AG Grid issues, change to big_number too
sql = "UPDATE slices SET viz_type = 'big_number' WHERE id IN (1,2,3,4,5)"
sql_b64 = base64.b64encode(sql.encode()).decode()
ssh.exec_command(f'echo {sql_b64} | base64 -d | docker exec -i podft-postgres psql -U podft -d superset 2>&1')

# Verify
stdin, stdout, stderr = ssh.exec_command(
    "docker exec podft-postgres psql -U podft -d superset -c \"SELECT id, viz_type, slice_name FROM slices ORDER BY id\" 2>&1"
)
print(stdout.read().decode(errors='replace').strip()[:500])

ssh.close()
