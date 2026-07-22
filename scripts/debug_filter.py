import paramiko, json
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=10)

# Check dashboard config with native filters
_, o, _ = ssh.exec_command(
    "docker exec podft-postgres psql -U podft -d superset -c "
    "\"SELECT id, slug, LEFT(json_metadata, 1000) as jm FROM dashboards WHERE id = 2\""
)
print('=== Dashboard 2 json_metadata ===')
print(o.read().decode(errors='replace'))

# Also check the dashboard in full
_, o2, _ = ssh.exec_command(
    "docker exec podft-postgres psql -U podft -d superset -c "
    "\"SELECT id, slug, dashboard_title FROM dashboards\""
)
print('\n=== All dashboards ===')
print(o2.read().decode(errors='replace'))

ssh.close()
