import paramiko, json
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=10)

# Get full json_metadata
_, o, _ = ssh.exec_command(
    "docker exec podft-postgres psql -U podft -d superset -t -c \"SELECT json_metadata FROM dashboards WHERE id = 2\""
)
jm_raw = o.read().decode(errors='replace').strip()
print('Raw length:', len(jm_raw))

jm = json.loads(jm_raw)

# Print native filter config
nf = jm.get('native_filter_configuration', [])
for i, f in enumerate(nf):
    print(f'\nFilter {i}:')
    print(json.dumps(f, indent=2, ensure_ascii=False))

# Check for required properties
for f in nf:
    missing = []
    for key in ['defaultDataMask', 'targets', 'controlValues', 'requiredFirst', 'scope']:
        if key not in f:
            missing.append(key)
    if missing:
        print(f'\nFilter {f.get("id")} missing: {missing}')

ssh.close()
