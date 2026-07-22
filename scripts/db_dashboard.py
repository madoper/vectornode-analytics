import paramiko, json

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

def run_sql(sql):
    cmd = f'docker exec podft-postgres psql -U podft -d superset -c "{sql}" 2>&1'
    stdin, stdout, stderr = ssh.exec_command(cmd)
    return stdout.read().decode(errors='replace').strip()

# Check current dashboard metadata
result = run_sql("SELECT id, dashboard_title, slug, json_metadata FROM dashboards WHERE id=2")
print("Current dashboard:")
print(result[:500])

# Build native filters JSON
native_filters = [
    {"id":"NF-year","filterType":"filter_select","column":"year","name":"Year","multiple":True,"dataset":3},
    {"id":"NF-region","filterType":"filter_select","column":"region","name":"Region","multiple":True,"dataset":3},
    {"id":"NF-okved","filterType":"filter_select","column":"okved_section","name":"Industry","multiple":True,"dataset":3},
    {"id":"NF-interp","filterType":"filter_select","column":"interpretation","name":"Interpretation","multiple":True,"dataset":3},
    {"id":"NF-crit","filterType":"filter_select","column":"criticality","name":"Criticality","multiple":True,"dataset":3},
    {"id":"NF-hypo","filterType":"filter_select","column":"hypothesis_code","name":"Hypothesis","multiple":True,"dataset":3},
]

json_meta = json.dumps({
    "native_filter_configuration": native_filters,
    "timed_refresh_immune_slices": [],
    "expanded_slices": {},
    "refresh_frequency": 0,
    "default_filters": "{}"
})

# Escape single quotes for SQL
json_meta_escaped = json_meta.replace("'", "''")

update_sql = f"""
UPDATE dashboards 
SET dashboard_title = 'VectorNode: Anomalies & Economic Signals',
    slug = 'vectornode-anomalies',
    description = 'Anomaly detection and economic signal analysis dashboard',
    json_metadata = '{json_meta_escaped}',
    changed_on = NOW()
WHERE id = 2
"""
result = run_sql(update_sql)
print(f"\nUpdate result: {result}")

# Verify
result2 = run_sql("SELECT id, dashboard_title, slug FROM dashboards WHERE id=2")
print(f"\nAfter update: {result2}")

ssh.close()
