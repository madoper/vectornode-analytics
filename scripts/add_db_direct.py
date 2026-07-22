import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

sql = """
INSERT INTO dbs (database_name, sqlalchemy_uri, expose_in_sqllab, allow_ctas, allow_run_async, created_on, changed_on)
VALUES (
  'Analytics (dbt)',
  'postgresql://dbt_user:dbt_pass@podft-postgres:5432/analytics',
  true, true, true,
  NOW(), NOW()
)
RETURNING id;
"""

cmd = f'docker exec podft-postgres psql -U podft -d superset -c "{sql}"'
stdin, stdout, stderr = ssh.exec_command(cmd)
print('INSERT result:', stdout.read().decode(errors='replace').strip())

# Verify
cmd2 = 'docker exec podft-postgres psql -U podft -d superset -c "SELECT id, database_name, sqlalchemy_uri FROM dbs"'
stdin2, stdout2, stderr2 = ssh.exec_command(cmd2)
print('Current DBs:', stdout2.read().decode(errors='replace').strip())

ssh.close()
