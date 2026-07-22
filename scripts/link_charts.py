import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

for cid in [1, 2, 3, 4]:
    cmd = f'docker exec podft-postgres psql -U podft -d superset -c "INSERT INTO dashboard_slices (dashboard_id, slice_id) SELECT 2, {cid} WHERE NOT EXISTS (SELECT 1 FROM dashboard_slices WHERE dashboard_id=2 AND slice_id={cid})" 2>&1'
    stdin, stdout, stderr = ssh.exec_command(cmd)
    print(f'Chart {cid}: {stdout.read().decode(errors="replace").strip()[:100]}')

# Verify
stdin2, stdout2, stderr2 = ssh.exec_command(
    'docker exec podft-postgres psql -U podft -d superset -c "SELECT ds.dashboard_id, ds.slice_id, s.slice_name FROM dashboard_slices ds JOIN slices s ON s.id = ds.slice_id WHERE ds.dashboard_id=2 ORDER BY ds.slice_id" 2>&1'
)
print(f'\nDashboard charts:')
print(stdout2.read().decode(errors='replace').strip())

ssh.close()
