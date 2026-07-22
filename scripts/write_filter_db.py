import paramiko, time, json, urllib.parse
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', port=22, username='root', password='8884&JKL%f75', timeout=10)

# Build filter value
filters_val = {
    "NATIVE_FILTER-93l_baaoiLKsUFesy8AyO": {
        "extraFormData": {
            "filters": [{"col": "year", "op": "IN", "val": [2024]}]
        },
        "filterState": {"label": "2024", "value": [2024]}
    }
}
entry = {"owner": 1, "value": json.dumps(filters_val)}
entry_json = json.dumps(entry)

# Write JSON to temp file on server
sftp = ssh.open_sftp()
f = sftp.file('/tmp/filter_update.json', 'w')
f.write(entry_json)
f.close()
sftp.close()

# Use Python in container to write to DB
_, o, _ = ssh.exec_command(
    'docker cp /tmp/filter_update.json podft-superset:/tmp/filter_update.json && '
    'docker exec podft-superset python3 -c "'
    'import psycopg2, json; '
    'with open(\"/tmp/filter_update.json\") as f: data = json.load(f); '
    'c = psycopg2.connect(host=\"podft-postgres\", user=\"podft\", password=\"podft-secret\", database=\"superset\"); '
    'cur = c.cursor(); '
    'cur.execute(\"UPDATE key_value SET value = %s WHERE id = 5\", (json.dumps(data).encode(),)); '
    'c.commit(); cur.close(); c.close(); '
    'print(\"OK\")"'
)
print('Write result:', o.read().decode(errors='replace'))

# Verify
_, o2, _ = ssh.exec_command(
    "docker exec podft-postgres psql -U podft -d superset -t -A -c \"SELECT convert_from(value, 'UTF8') FROM key_value WHERE id = 5\""
)
verify = o2.read().decode(errors='replace')
print('Verify:', verify[:200])

# Now test the chart query
_, auth, _ = ssh.exec_command(
    'curl -s -X POST http://127.0.0.1:8088/api/v1/security/login -H "Content-Type: application/json" -d \'{"username":"admin","password":"admin","provider":"db"}\''
)
token = json.loads(auth.read().decode(errors='replace'))["access_token"]

fd = urllib.parse.quote('{"slice_id":4}')
_, co, _ = ssh.exec_command(
    'curl -s -w "\nHTTP_%{http_code}" -X POST "http://127.0.0.1:8088/api/v1/chart/data?form_data=' + fd + '&dashboard_id=2" '
    '-H "Content-Type: application/json" '
    '-H "Authorization: Bearer ' + token + '" '
    '-H "Referer: https://bi.vectornode.ru/superset/dashboard/vectornode-anomalies/?native_filters_key=on3j7Uo8xSs"'
)
out = co.read().decode(errors='replace')
print('\nChart result:')
if 'year = 2024' in out or 'year IN' in out:
    print('   FILTER APPLIED!')
    idx = out.index('"query"')
    print('   ' + out[idx:idx+300])
else:
    if '"query"' in out:
        idx = out.index('"query"')
        print('   ' + out[idx:idx+250])
    else:
        print('   ', out[:400])

# Also check debug logs
_, so2, _ = ssh.exec_command('docker logs podft-superset --since 30s 2>&1 | grep "FILTER_" | tail -8')
print('\nDebug:')
print(so2.read().decode(errors='replace'))

ssh.close()
