import paramiko, time, json, urllib.parse
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', port=22, username='root', password='8884&JKL%f75', timeout=10)

# Build filter value with year=2024 filter
filter_value = json.dumps({
    "NATIVE_FILTER-93l_baaoiLKsUFesy8AyO": {
        "id": "NATIVE_FILTER-93l_baaoiLKsUFesy8AyO",
        "extraFormData": {
            "filters": [{"col": "year", "op": "IN", "val": [2024]}]
        },
        "filterState": {"label": "2024", "value": [2024]},
        "ownState": {}
    }
})

# Write to key_value DB entry (id=5)
entry_value = json.dumps({"owner": 1, "value": filter_value})

# Update using psql
cmd = "docker exec podft-postgres psql -U podft -d superset -c \"UPDATE key_value SET value = decode('" + entry_value.replace("'", "''") + "', 'escape') WHERE id = 5\""
_, o, _ = ssh.exec_command(cmd)
print('DB update:', o.read().decode(errors='replace'))

# Verify
cmd2 = "docker exec podft-postgres psql -U podft -d superset -t -A -c \"SELECT convert_from(value, 'UTF8') FROM key_value WHERE id = 5\""
_, o2, _ = ssh.exec_command(cmd2)
print('Verify:', o2.read().decode(errors='replace')[:200])

# Login and test chart
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
elif 'HTTP_200' in out:
    print('   200 OK')
    if '"query"' in out:
        idx = out.index('"query"')
        print('   ' + out[idx:idx+250])
else:
    print('   ', out[:400])

ssh.close()
