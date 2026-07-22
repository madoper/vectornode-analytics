import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

sftp = ssh.open_sftp()
sftp.put(r'D:\project\FRS_TEST\scripts\superset_dash.sql', '/tmp/superset_dash.sql')
sftp.close()

stdin, stdout, stderr = ssh.exec_command(
    'docker exec -i podft-postgres psql -U podft -d superset < /tmp/superset_dash.sql 2>&1'
)
print(stdout.read().decode(errors='replace').strip())

# Verify
stdin2, stdout2, stderr2 = ssh.exec_command(
    "docker exec podft-postgres psql -U podft -d superset -c \"SELECT id, dashboard_title, published FROM dashboards ORDER BY id\" 2>&1"
)
print('\nDashboards:')
print(stdout2.read().decode(errors='replace').strip())

# Verify tables
stdin3, stdout3, stderr3 = ssh.exec_command(
    "docker exec podft-postgres psql -U podft -d superset -c \"SELECT id, table_name, database_id, schema FROM tables\" 2>&1"
)
print('\nDatasets:')
print(stdout3.read().decode(errors='replace').strip())

ssh.close()
