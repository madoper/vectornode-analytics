import paramiko, json
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=10)

# Get dashboard 2 json_metadata
_, o, _ = ssh.exec_command(
    "docker exec podft-postgres psql -U podft -d superset -t -c \"SELECT json_metadata FROM dashboards WHERE id = 2\""
)
jm = json.loads(o.read().decode(errors='replace').strip())

# Also check dashboard 1 (Anomaly Detection Dashboard) for comparison
_, o1, _ = ssh.exec_command(
    "docker exec podft-postgres psql -U podft -d superset -t -c \"SELECT json_metadata FROM dashboards WHERE id = 1\""
)
jm1_str = o1.read().decode(errors='replace').strip()
print('Dashboard 1 has native filters:', 'native_filter_configuration' in jm1_str)

# Print full native filter config from dashboard 2
for i, nf in enumerate(jm.get('native_filter_configuration', [])):
    print(f'\n=== Filter {i}: {nf["name"]} ===')
    for k, v in nf.items():
        print(f'  {k}: {json.dumps(v, ensure_ascii=False)[:200]}')

ssh.close()
