import paramiko, json, base64
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=10)

# Get current metadata
_, o, _ = ssh.exec_command(
    "docker exec podft-postgres psql -U podft -d superset -t -c \"SELECT json_metadata FROM dashboards WHERE id = 2\""
)
jm = json.loads(o.read().decode(errors='replace').strip())

# Remove all native filters
jm['native_filter_configuration'] = []
jm.pop('globalFilters', None)

# Update via base64
encoded = base64.b64encode(json.dumps(jm).encode()).decode()
_, o2, _ = ssh.exec_command(
    f"docker exec podft-postgres psql -U podft -d superset -c "
    f"\"UPDATE dashboards SET json_metadata = convert_from(decode('{encoded}', 'base64'), 'UTF8') WHERE id = 2\""
)
print('Update:', o2.read().decode(errors='replace'))

# Verify
_, o3, _ = ssh.exec_command(
    "docker exec podft-postgres psql -U podft -d superset -t -c "
    "\"SELECT json_metadata->'native_filter_configuration' FROM dashboards WHERE id = 2\""
)
print('Filters after:', o3.read().decode(errors='replace').strip())

ssh.close()
