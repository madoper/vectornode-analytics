import paramiko, json
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=10)

_, o, _ = ssh.exec_command(
    "docker exec podft-postgres psql -U podft -d superset -t -c \"SELECT json_metadata FROM dashboards WHERE id = 2\""
)
jm = json.loads(o.read().decode(errors='replace').strip())

# Fix each filter - remove problematic scope, add proper defaults
for nf in jm['native_filter_configuration']:
    # Reset scope to safe values
    nf['scope'] = {
        'rootPath': ['ROOT_ID'],
        'excluded': []
    }
    # Add missing fields
    nf['cascadeParentIds'] = []
    nf['defaultValue'] = None
    nf['sqlExpression'] = None
    nf['behavior'] = 'NATIVE_FILTER'
    # Fix controlValues
    nf['controlValues'] = {
        'enableEmptyFilter': False,
        'defaultToFirstItem': False,
        'inverseSelection': False,
        'multiSelect': True,
        'searchAllOptions': False,
    }
    # Set initial defaultDataMask
    nf['defaultDataMask'] = {
        'filterState': {'value': None},
        'dataMask': {},
        'extraFormData': {},
    }

# Write
sftp = ssh.open_sftp()
f = sftp.file('/tmp/jm_v4.json', 'w')
f.write(json.dumps(jm))
f.close()
sftp.close()

# Deploy
_, o2, _ = ssh.exec_command("docker cp /tmp/jm_v4.json podft-postgres:/tmp/jm_v4.json")
_, o3, _ = ssh.exec_command(
    "docker exec podft-postgres psql -U podft -d superset -c "
    "\"UPDATE dashboards SET json_metadata = pg_read_file('/tmp/jm_v4.json') WHERE id = 2\""
)
print('Update done')

# Quick verify - get first filter id and name
_, o4, _ = ssh.exec_command(
    "docker exec podft-postgres psql -U podft -d superset -t -c "
    "\"SELECT json_metadata->'native_filter_configuration'->0->>'id', json_metadata->'native_filter_configuration'->0->>'name' FROM dashboards WHERE id = 2\""
)
print(o4.read().decode(errors='replace'))

ssh.close()
