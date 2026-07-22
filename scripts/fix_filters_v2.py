import paramiko, json, base64
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=10)

# Check current filter config
_, o, _ = ssh.exec_command(
    "docker exec podft-postgres psql -U podft -d superset -t -c "
    "\"SELECT json_metadata->'native_filter_configuration'->0 FROM dashboards WHERE id = 2\""
)
raw = o.read().decode(errors='replace').strip()
print('Filter 0 raw:', raw[:200] if raw else 'EMPTY')

# Get full json_metadata length
_, o2, _ = ssh.exec_command(
    "docker exec podft-postgres psql -U podft -d superset -t -c "
    "\"SELECT LENGTH(json_metadata::text) FROM dashboards WHERE id = 2\""
)
print('Metadata length:', o2.read().decode(errors='replace').strip())

# Update via base64
_, o3, _ = ssh.exec_command(
    "docker exec podft-postgres psql -U podft -d superset -t -c \"SELECT json_metadata FROM dashboards WHERE id = 2\""
)
jm = json.loads(o3.read().decode(errors='replace').strip())

# Fix each filter properly
for nf in jm['native_filter_configuration']:
    nf.update({
        'cascadeParentIds': [],
        'defaultValue': None,
        'sqlExpression': None,
        'behavior': 'NATIVE_FILTER',
        'scope': {'rootPath': ['ROOT_ID'], 'excluded': []},
        'controlValues': {
            'enableEmptyFilter': False,
            'defaultToFirstItem': False,
            'inverseSelection': False,
            'multiSelect': True,
            'searchAllOptions': False,
        },
        'defaultDataMask': {
            'filterState': {'value': None},
            'dataMask': {},
            'extraFormData': {},
        },
        'requiredFirst': False,
    })

# Encode and update
encoded = base64.b64encode(json.dumps(jm).encode()).decode()

_, o4, _ = ssh.exec_command(
    f"docker exec podft-postgres psql -U podft -d superset -c "
    f"\"UPDATE dashboards SET json_metadata = convert_from(decode('{encoded}', 'base64'), 'UTF8') WHERE id = 2\""
)
print('Base64 update:', o4.read().decode(errors='replace'))

# Verify
_, o5, _ = ssh.exec_command(
    "docker exec podft-postgres psql -U podft -d superset -t -c "
    "\"SELECT json_metadata->'native_filter_configuration'->0->>'scope' FROM dashboards WHERE id = 2\""
)
print('Scope:', o5.read().decode(errors='replace').strip()[:200])

ssh.close()
