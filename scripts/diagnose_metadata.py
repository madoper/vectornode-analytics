import paramiko, json
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=10)

# Get full json_metadata
_, o, _ = ssh.exec_command(
    "docker exec podft-postgres psql -U podft -d superset -t -c \"SELECT json_metadata FROM dashboards WHERE id = 2\""
)
raw = o.read().decode(errors='replace').strip()
print('Raw metadata length:', len(raw))
print('First 500 chars:', raw[:500])
print('...')
print('Last 300 chars:', raw[-300:])

# Try to parse
try:
    jm = json.loads(raw)
    print('\nParsed successfully!')
    print('Keys:', list(jm.keys()))
    nf_len = len(jm.get('native_filter_configuration', []))
    print('Native filters count:', nf_len)
    if nf_len > 0:
        print('Filter 0:', jm['native_filter_configuration'][0])
except json.JSONDecodeError as e:
    print(f'\nJSON error: {e}')
    # Try to find where JSON breaks
    for i in range(0, len(raw), 100):
        try:
            json.loads(raw[:i])
        except json.JSONDecodeError:
            print(f'JSON breaks around position {i}')
            print(f'Context: ...{raw[max(0,i-50):i+50]}...')
            break

ssh.close()
