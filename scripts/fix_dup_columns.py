import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', port=22, username='root', password='8884&JKL%f75', timeout=10)

# Check duplicates in Superset table_columns
_, o, _ = ssh.exec_command(
    "docker exec podft-postgres psql -U podft -d superset -c "
    "\"SELECT column_name, count(1) AS cnt FROM table_columns WHERE table_id = 3 GROUP BY column_name HAVING count(1) > 1\""
)
print('Duplicate columns in Superset:')
print(o.read().decode(errors='replace'))

# Remove duplicates
_, o2, _ = ssh.exec_command(
    "docker exec podft-postgres psql -U podft -d superset -c "
    "\"DELETE FROM table_columns WHERE id IN (SELECT id FROM (SELECT id, ROW_NUMBER() OVER (PARTITION BY table_id, column_name ORDER BY id) AS rn FROM table_columns WHERE table_id = 3) t WHERE t.rn > 1)\""
)
print('\nDelete duplicates:', o2.read().decode(errors='replace'))

# Verify
_, o3, _ = ssh.exec_command(
    "docker exec podft-postgres psql -U podft -d superset -c "
    "\"SELECT count(1) FROM table_columns WHERE table_id = 3\""
)
print('\nTotal columns after cleanup:', o3.read().decode(errors='replace'))

# Refresh dataset via API
_, auth, _ = ssh.exec_command(
    'curl -s -X POST http://127.0.0.1:8088/api/v1/security/login '
    '-H "Content-Type: application/json" '
    '-d \'{"username":"admin","password":"admin","provider":"db"}\''
)
import json
token = json.loads(auth.read().decode(errors='replace'))["access_token"]

_, o4, _ = ssh.exec_command(
    'curl -s -w " HTTP_%{http_code}" -X PUT "http://127.0.0.1:8088/api/v1/dataset/3/refresh" '
    '-H "Content-Type: application/json" '
    '-H "Authorization: Bearer ' + token + '" '
    '-d \'{"datasource_type": "table"}\''
)
print('\nRefresh dataset:', o4.read().decode(errors='replace')[:200])

# Test chart
fd = '{"slice_id":1}'
import urllib.parse
_, o5, _ = ssh.exec_command(
    'curl -s -w "\nHTTP_%{http_code}" -X POST "http://127.0.0.1:8088/api/v1/chart/data?form_data=' + urllib.parse.quote(fd) + '" '
    '-H "Content-Type: application/json" '
    '-H "Authorization: Bearer ' + token + '"'
)
out = o5.read().decode(errors='replace')
if 'Duplicate column' in out:
    print('\nChart 1 ERROR:', out[:300])
    # Check query_context for charts
    for cid in [1, 2, 3, 4, 5, 6]:
        _, o6, _ = ssh.exec_command(
            "docker exec podft-postgres psql -U podft -d superset -t -A -c "
            "\"SELECT query_context FROM slices WHERE id = " + str(cid) + "\""
        )
        qc_raw = o6.read().decode(errors='replace').strip()
        if 'criticality' in qc_raw:
            # Count occurrences
            count_crit = qc_raw.count('criticality')
            print(f'  Chart {cid}: criticality appears {count_crit} times in query_context')
else:
    print('\nChart 1 OK:', out[:200] if 'HTTP_200' in out else out[:200])

ssh.close()
