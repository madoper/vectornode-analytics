import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=10)

# Check Superset database connection URI
_, o, _ = ssh.exec_command(
    'grep SQLALCHEMY_DATABASE_URI /opt/podft/infra/superset-init/superset_config.py 2>/dev/null || '
    'docker exec podft-superset env | grep DATABASE 2>/dev/null || '
    'echo "not found"'
)
print('Superset DB URI:')
print(o.read().decode(errors='replace'))

# Check who owns the view
_, o2, _ = ssh.exec_command(
    'docker exec podft-postgres psql -U podft -d analytics -c '
    '"SELECT schemaname, viewname, viewowner FROM pg_views WHERE viewname = ''v_company_dashboard''"'
)
print('\nView owner:')
print(o2.read().decode(errors='replace'))

# Check Superset datasource connection
_, o3, _ = ssh.exec_command(
    'docker exec podft-postgres psql -U podft -d analytics -c '
    '"SELECT id, database_name, sqlalchemy_uri FROM dbs" 2>/dev/null'
)
print('\nSuperset DBs:')
print(o3.read().decode(errors='replace')[:2000])

# Grant access to analytics schema and view
_, o4, _ = ssh.exec_command(
    'docker exec podft-postgres psql -U podft -d analytics << EOF\n'
    'GRANT USAGE ON SCHEMA analytics TO PUBLIC;\n'
    'GRANT SELECT ON analytics.v_company_dashboard TO PUBLIC;\n'
    'GRANT SELECT ON ALL TABLES IN SCHEMA analytics TO PUBLIC;\n'
    'EOF'
)
print('\nGrant result:')
print(o4.read().decode(errors='replace'))

ssh.close()
