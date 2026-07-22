import paramiko, json
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', port=22, username='root', password='8884&JKL%f75', timeout=10)

for cid in [1, 3]:
    _, o, _ = ssh.exec_command(
        "docker exec podft-postgres psql -U podft -d superset -t -A -c "
        "\"SELECT query_context FROM slices WHERE id = " + str(cid) + "\""
    )
    qc = json.loads(o.read().decode(errors='replace').strip())
    queries = qc.get('queries', [])
    print(f'=== Chart {cid} queries ===')
    for qi, q in enumerate(queries):
        print(f'  Query {qi}:')
        print(f'    groupby: {q.get("groupby", [])}')
        print(f'    columns: {q.get("columns", [])}')
        for mi, m in enumerate(q.get('metrics', [])):
            print(f'    metric {mi}: {m.get("label", m.get("column", {}).get("column_name"))}')
        for mi, m in enumerate(q.get('orderby', [])):
            print(f'    orderby {mi}: label={m[0].get("label", m[0].get("column", {}).get("column_name"))} dir={m[1]}')
    print()

ssh.close()
