import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

stdin, stdout, stderr = ssh.exec_command("docker exec podft-postgres psql -U podft -d superset -c \"SELECT json_metadata FROM dashboards WHERE id=2\" -A -t 2>&1")
res = stdout.read().decode(errors='replace').strip()
print('json_metadata:' if len(res) < 50 else 'has content:', res[:200])

# Also check dashboard now - just verify title
stdin2, stdout2, stderr2 = ssh.exec_command("docker exec podft-postgres psql -U podft -d superset -c \"SELECT dashboard_title, slug FROM dashboards WHERE id=2\" 2>&1")
print('\nDashboard:', stdout2.read().decode(errors='replace').strip())

ssh.close()
