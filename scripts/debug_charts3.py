import paramiko, json
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=10)

# Full query_context and viz_type for all charts
_, o, _ = ssh.exec_command(
    "docker exec podft-postgres psql -U podft -d superset -c "
    "\"SELECT id, slice_name, viz_type, LEFT(query_context, 500) as qc FROM slices ORDER BY id\""
)
print('=== ALL CHARTS ===')
print(o.read().decode(errors='replace'))

# Also check chart params
_, o2, _ = ssh.exec_command(
    "docker exec podft-postgres psql -U podft -d superset -c "
    "\"SELECT id, slice_name, viz_type, LEFT(params, 200) as params FROM slices ORDER BY id\""
)
print('\n=== CHART PARAMS ===')
print(o2.read().decode(errors='replace'))

ssh.close()
