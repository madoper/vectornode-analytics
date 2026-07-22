import paramiko, json
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', port=22, username='root', password='8884&JKL%f75', timeout=10)

for cid, dup_col in [(1, 'criticality'), (3, 'hypothesis_code')]:
    # Read query_context
    _, o, _ = ssh.exec_command(
        "docker exec podft-postgres psql -U podft -d superset -t -A -c "
        "\"SELECT query_context FROM slices WHERE id = " + str(cid) + "\""
    )
    qc = json.loads(o.read().decode(errors='replace').strip())
    
    # Fix: remove duplicate column entries
    for query in qc.get('queries', []):
        cols = query.get('columns', [])
        unique_cols = []
        seen_labels = set()
        for col in cols:
            if isinstance(col, str):
                label = col
            elif isinstance(col, dict):
                label = col.get('label', col.get('sqlExpression', ''))
            else:
                label = str(col)
            if label not in seen_labels:
                seen_labels.add(label)
                unique_cols.append(col)
        query['columns'] = unique_cols
    
    # Update in DB
    updated_qc = json.dumps(qc)
    safe_qc = updated_qc.replace("'", "''")
    _, o2, _ = ssh.exec_command(
        "docker exec podft-postgres psql -U podft -d superset -c "
        "\"UPDATE slices SET query_context = '" + safe_qc + "' WHERE id = " + str(cid) + "\""
    )
    print(f'Chart {cid}: {o2.read().decode(errors="replace").strip()}')

# Test charts
_, auth, _ = ssh.exec_command(
    'curl -s -X POST http://127.0.0.1:8088/api/v1/security/login '
    '-H "Content-Type: application/json" '
    '-d \'{"username":"admin","password":"admin","provider":"db"}\''
)
token = json.loads(auth.read().decode(errors='replace'))["access_token"]

import urllib.parse
for cid in [1, 3]:
    fd = urllib.parse.quote(f'{{"slice_id":{cid}}}')
    _, co, _ = ssh.exec_command(
        'curl -s -w "\nHTTP_%{http_code}" -X POST "http://127.0.0.1:8088/api/v1/chart/data?form_data=' + fd + '" '
        '-H "Content-Type: application/json" '
        '-H "Authorization: Bearer ' + token + '"'
    )
    out = co.read().decode(errors='replace')
    if 'HTTP_200' in out or 'HTTP_302' in out:
        print(f'  Chart {cid}: OK')
    else:
        print(f'  Chart {cid}: {out[:200]}')

ssh.close()
