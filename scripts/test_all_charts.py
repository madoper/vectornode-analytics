import paramiko, json, urllib.parse
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', port=22, username='root', password='8884&JKL%f75', timeout=10)

_, auth, _ = ssh.exec_command(
    'curl -s -X POST http://127.0.0.1:8088/api/v1/security/login '
    '-H "Content-Type: application/json" '
    '-d \'{"username":"admin","password":"admin","provider":"db"}\''
)
token = json.loads(auth.read().decode(errors='replace'))["access_token"]

# Test ALL charts with dashboard context
for cid in range(1, 7):
    fd = urllib.parse.quote(f'{{"slice_id":{cid}}}')
    _, co, _ = ssh.exec_command(
        'curl -s -w "\nHTTP_%{http_code}" -X POST "http://127.0.0.1:8088/api/v1/chart/data?form_data=' + fd + '&dashboard_id=2" '
        '-H "Content-Type: application/json" '
        '-H "Authorization: Bearer ' + token + '" '
        '-H "Referer: https://bi.vectornode.ru/superset/dashboard/vectornode-anomalies/?native_filters_key=on3j7Uo8xSs"'
    )
    out = co.read().decode(errors='replace')
    if 'Duplicate column' in out or 'Error' in out or 'HTTP_400' in out:
        print(f'Chart {cid}: ERROR - {out[:200]}')
        # Get query_context for this chart
        _, o2, _ = ssh.exec_command(
            "docker exec podft-postgres psql -U podft -d superset -t -A -c "
            "\"SELECT query_context FROM slices WHERE id = " + str(cid) + "\""
        )
        qc = o2.read().decode(errors='replace').strip()
        # Find the label that's causing issues
        print(f'  query_context length: {len(qc)}')
        if 'criticality' in qc:
            # Count all labels in queries
            import re
            labels = re.findall(r'"label": "([^"]+)"', qc)
            labels += re.findall(r'"groupby": \[([^\]]+)\]', qc)
            print(f'  labels/groups found:')
            for l in labels:
                print(f'    {l}')
    else:
        print(f'Chart {cid}: OK')

ssh.close()
