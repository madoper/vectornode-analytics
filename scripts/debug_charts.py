import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=10)

# Check view columns
_, o, _ = ssh.exec_command(
    'docker exec podft-postgres psql -U podft -d analytics -c '
    '"SELECT column_name, data_type FROM information_schema.columns WHERE table_schema=''analytics'' AND table_name=''v_company_dashboard'' ORDER BY ordinal_position"'
)
print('=== VIEW COLUMNS ===')
print(o.read().decode(errors='replace'))

# Check query_context for each chart
_, o2, _ = ssh.exec_command(
    'docker exec podft-postgres psql -U podft -d superset -c '
    '"SELECT id, slice_name, LEFT(query_context, 200) as qc_short FROM slices ORDER BY id"'
)
print('\n=== CHART QUERY CONTEXTS ===')
print(o2.read().decode(errors='replace'))

ssh.close()
