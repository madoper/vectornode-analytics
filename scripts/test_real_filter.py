import paramiko, time, json, urllib.parse
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', port=22, username='root', password='8884&JKL%f75', timeout=10)

# Login
_, auth, _ = ssh.exec_command(
    'curl -s -X POST http://127.0.0.1:8088/api/v1/security/login -H "Content-Type: application/json" -d \'{"username":"admin","password":"admin","provider":"db"}\''
)
token = json.loads(auth.read().decode(errors='replace'))["access_token"]

# Set a filter via the API (simulate selecting year=2024)
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

# PUT to filter_state
_, setf, _ = ssh.exec_command(
    'curl -s -w "\nHTTP_%{http_code}" -X PUT "http://127.0.0.1:8088/api/v1/dashboard/2/filter_state/on3j7Uo8xSs?tab_id=2" '
    '-H "Content-Type: application/json" '
    '-H "Authorization: Bearer ' + token + '" '
    '-d \'' + json.dumps({"value": filter_value}) + '\''
)
print('Set filter:', setf.read().decode(errors='replace')[:100])

# Now test chart POST with filter
time.sleep(2)
fd = urllib.parse.quote('{"slice_id":4}')
_, co, _ = ssh.exec_command(
    'curl -s -w "\nHTTP_%{http_code}" -X POST "http://127.0.0.1:8088/api/v1/chart/data?form_data=' + fd + '&dashboard_id=2" '
    '-H "Content-Type: application/json" '
    '-H "Authorization: Bearer ' + token + '" '
    '-H "Referer: https://bi.vectornode.ru/superset/dashboard/vectornode-anomalies/?native_filters_key=on3j7Uo8xSs"'
)
out = co.read().decode(errors='replace')
print('\nChart with filter:')
if 'year = 2024' in out:
    print('   FILTER APPLIED! year = 2024 found in query!')
    idx = out.index('"query"')
    print('   ' + out[idx:idx+300])
elif 'HTTP_200' in out:
    print('   200 OK')
    if '"query"' in out:
        idx = out.index('"query"')
        print('   Query:', out[idx:idx+200])
else:
    print('   ', out[:400])

# Check debug
_, so2, _ = ssh.exec_command('docker logs podft-superset --since 30s 2>&1 | grep "FILTER_" | tail -8')
print('\nDebug:')
print(so2.read().decode(errors='replace'))

ssh.close()
