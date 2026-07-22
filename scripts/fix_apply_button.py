import paramiko, json
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=10)

# Dashboard 2 native filters need cascadeParentIds for Apply button to work
_, o, _ = ssh.exec_command(
    "docker exec podft-postgres psql -U podft -d superset -t -c \"SELECT json_metadata FROM dashboards WHERE id = 2\""
)
jm = json.loads(o.read().decode(errors='replace').strip())

# Add missing properties to each filter
for nf in jm['native_filter_configuration']:
    if 'cascadeParentIds' not in nf:
        nf['cascadeParentIds'] = []
    if 'defaultValue' not in nf:
        nf['defaultValue'] = None
    if 'sqlExpression' not in nf:
        nf['sqlExpression'] = None
    if 'behavior' not in nf:
        nf['behavior'] = 'NATIVE_FILTER'
    # Fix controlValues
    nf['controlValues'] = {
        'enableEmptyFilter': False,
        'defaultToFirstItem': False,
        'inverseSelection': False,
        'multiSelect': True,
        'searchAllOptions': False,
    }

# Also add a global_filters config if missing
if 'globalFilters' not in jm:
    jm['globalFilters'] = {}

# Write updated metadata
sftp = ssh.open_sftp()
f = sftp.file('/tmp/jm_v3.json', 'w')
f.write(json.dumps(jm))
f.close()
sftp.close()

# Copy to container and update
_, o2, _ = ssh.exec_command("docker cp /tmp/jm_v3.json podft-postgres:/tmp/jm_v3.json")
print('cp:', o2.read().decode(errors='replace'))

_, o3, _ = ssh.exec_command(
    "docker exec podft-postgres psql -U podft -d superset -c "
    "\"UPDATE dashboards SET json_metadata = pg_read_file('/tmp/jm_v3.json') WHERE id = 2\""
)
print('update:', o3.read().decode(errors='replace'))

# Verify
_, o4, _ = ssh.exec_command(
    "docker exec podft-postgres psql -U podft -d superset -t -c "
    "\"SELECT json_metadata->'native_filter_configuration'->0 FROM dashboards WHERE id = 2\""
)
nf0 = json.loads(o4.read().decode(errors='replace').strip())
print('\nUpdated filter 0 keys:', list(nf0.keys()))

ssh.close()
