import paramiko, json, time
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', port=22, username='root', password='8884&JKL%f75', timeout=10)

# 1. Get raw filter config to see the column field
_, o, _ = ssh.exec_command(
    "docker exec podft-postgres psql -U podft -d superset -t -c "
    "\"SELECT json_metadata->'native_filter_configuration'->0 FROM dashboards WHERE id = 2\""
)
raw = o.read().decode(errors='replace').strip()
print('Filter raw:', raw[:500])

nf = json.loads(raw)
print('\nFilter keys:', list(nf.keys()))

# Fix column if missing
if 'column' not in nf or not nf.get('column'):
    nf['column'] = 'year'
    print('\nFixed column to: year')
else:
    print('\nColumn:', nf.get('column'))

# Update the dashboard json_metadata with fixed filter
_, o2, _ = ssh.exec_command(
    "docker exec podft-postgres psql -U podft -d superset -t -c \"SELECT json_metadata FROM dashboards WHERE id = 2\""
)
jm_raw = o2.read().decode(errors='replace').strip()
jm = json.loads(jm_raw)

# Update filter config
jm['native_filter_configuration'][0] = nf

# Write back to DB
sftp = ssh.open_sftp()
f = sftp.file('/tmp/jm_fixed.json', 'w')
f.write(json.dumps(jm))
f.close()
sftp.close()

_, o3, _ = ssh.exec_command("docker cp /tmp/jm_fixed.json podft-postgres:/tmp/jm_fixed.json")
_, o4, _ = ssh.exec_command(
    "docker exec podft-postgres psql -U podft -d superset -c "
    "\"UPDATE dashboards SET json_metadata = pg_read_file('/tmp/jm_fixed.json') WHERE id = 2\""
)
print('Dashboard updated:', o4.read().decode(errors='replace'))

# Deploy middleware
V = '/var/lib/docker/volumes/podft_superset_data/_data'
sftp2 = ssh.open_sftp()
sftp2.put(r'D:\project\FRS_TEST\scripts\superset_config_clean.py', '/opt/podft/infra/superset-init/superset_config.py')
sftp2.put(r'D:\project\FRS_TEST\scripts\superset_config_clean.py', f'{V}/superset_config.py')
sftp2.close()
ssh.exec_command(f'find {V} -name "*.pyc" -delete; find {V} -name "__pycache__" -exec rm -rf {{}} +')

_, o5, _ = ssh.exec_command('docker restart podft-superset')
print('Restarting Superset...')
time.sleep(3)

ssh.close()
