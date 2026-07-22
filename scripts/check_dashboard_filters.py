import paramiko, json
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', port=22, username='root', password='8884&JKL%f75', timeout=10)

# Check dashboard json_metadata for native filters
cmd = "docker exec podft-postgres psql -U podft -d superset -t -c \"SELECT json_metadata FROM dashboards WHERE id = 2\""
_, o, _ = ssh.exec_command(cmd)
raw = o.read().decode(errors='replace').strip()
jm = json.loads(raw)

nf = jm.get('native_filter_configuration', [])
print(f'Native filters count: {len(nf)}')
for i, f in enumerate(nf):
    print(f'\nFilter {i}: id={f.get("id")} name={f.get("name")} column={f.get("column")}')
    print(f'  filterType: {f.get("filterType")}')
    print(f'  controlValues: {json.dumps(f.get("controlValues", {}))}')
    print(f'  defaultDataMask: {json.dumps(f.get("defaultDataMask", {}))}')

# Also check the new chart (id 7)
cmd2 = "docker exec podft-postgres psql -U podft -d superset -c \"SELECT id, slice_name, viz_type, datasource_id FROM slices WHERE id = 7\""
_, o2, _ = ssh.exec_command(cmd2)
print('\nChart 7:', o2.read().decode(errors='replace'))

ssh.close()
