import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

# Check charts
stdin, stdout, stderr = ssh.exec_command("docker exec podft-postgres psql -U podft -d superset -c \"SELECT id, slice_name, viz_type, params::text FROM slices WHERE id IN (1,2,3,4)\" 2>&1")
print('Charts:')
print(stdout.read().decode(errors='replace').strip()[:1000])

# Check dashboard-chart links
stdin2, stdout2, stderr2 = ssh.exec_command("docker exec podft-postgres psql -U podft -d superset -c \"SELECT dashboard_id, slice_id FROM dashboard_slices WHERE dashboard_id=2 ORDER BY slice_id\" 2>&1")
print('\nDashboard charts:')
print(stdout2.read().decode(errors='replace').strip())

ssh.close()
