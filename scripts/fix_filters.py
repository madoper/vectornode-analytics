import paramiko, json
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=10)

# Get dashboard metadata
_, o, _ = ssh.exec_command(
    "docker exec podft-postgres psql -U podft -d superset -t -c \"SELECT json_metadata FROM dashboards WHERE id = 2\""
)
jm = json.loads(o.read().decode(errors='replace').strip())

# Get chart IDs for targets
_, o2, _ = ssh.exec_command(
    "docker exec podft-postgres psql -U podft -d superset -t -c \"SELECT id FROM slices ORDER BY id\""
)
chart_ids = [int(line.strip()) for line in o2.read().decode(errors='replace').strip().split('\n') if line.strip()]
print('Chart IDs:', chart_ids)

# Fix native filters - add required properties
for nf in jm['native_filter_configuration']:
    nf['controlValues'] = {
        'enableEmptyFilter': False,
        'defaultToFirstItem': False,
        'inverseSelection': False,
        'multiSelect': nf.get('multiple', True),
        'searchAllOptions': True,
    }
    nf['requiredFirst'] = False
    nf['defaultDataMask'] = {
        'filterState': {},
        'dataMask': {},
        'extraFormData': {},
    }
    # Targets: all chart IDs
    nf['targets'] = [{'datasetId': 3, 'column': {'name': nf['column']}}]
    nf['scope'] = {
        'rootPath': ['ROOT_ID'],
        'excluded': [0],
    }

# Write updated metadata
sftp = ssh.open_sftp()
f = sftp.file('/tmp/jm_updated.json', 'w')
f.write(json.dumps(jm))
f.close()
sftp.close()

# Copy to container and update
_, o3, _ = ssh.exec_command("docker cp /tmp/jm_updated.json podft-postgres:/tmp/jm_updated.json")
print('cp:', o3.read().decode(errors='replace'))

_, o4, _ = ssh.exec_command(
    "docker exec podft-postgres psql -U podft -d superset -c "
    "\"UPDATE dashboards SET json_metadata = pg_read_file('/tmp/jm_updated.json') WHERE id = 2\""
)
print('update:', o4.read().decode(errors='replace'))

# Also set position_json for the dashboard so the native filter panel renders
# position_json defines where charts and filters are placed
_, o5, _ = ssh.exec_command(
    "docker exec podft-postgres psql -U podft -d superset -t -c \"SELECT position_json IS NULL FROM dashboards WHERE id = 2\""
)
print('position_json is null:', o5.read().decode(errors='replace').strip())

# Verify updated filter config
_, o6, _ = ssh.exec_command(
    "docker exec podft-postgres psql -U podft -d superset -t -c "
    "\"SELECT json_metadata->'native_filter_configuration'->0 FROM dashboards WHERE id = 2\""
)
print('\nUpdated filter 0:')
print(json.dumps(json.loads(o6.read().decode(errors='replace').strip().split('\n')[-1]), indent=2, ensure_ascii=False)[:500])

ssh.close()
