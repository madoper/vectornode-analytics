import paramiko, json, urllib.parse
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', port=22, username='root', password='8884&JKL%f75', timeout=10)

# Check filter state entries
_, o, _ = ssh.exec_command(
    "docker exec podft-postgres psql -U podft -d superset -t -A -c \"SELECT id, uuid, LEFT(convert_from(value,'UTF8'), 400) FROM key_value WHERE id IN (5,6) ORDER BY id\""
)
print('Filter state entries:')
print(o.read().decode(errors='replace'))

# Login and test chart with filter
_, auth, _ = ssh.exec_command(
    "curl -s -X POST http://127.0.0.1:8088/api/v1/security/login -H 'Content-Type: application/json' -d '{\"username\":\"admin\",\"password\":\"admin\",\"provider\":\"db\"}'"
)
token = json.loads(auth.read().decode(errors='replace'))["access_token"]

fd = urllib.parse.quote('{"slice_id":1}')
_, co, _ = ssh.exec_command(
    'curl -s -w "\nHTTP_%{http_code}" -X POST "http://127.0.0.1:8088/api/v1/chart/data?form_data=' + fd + '&dashboard_id=2" '
    '-H "Content-Type: application/json" '
    '-H "Authorization: Bearer ' + token + '" '
    '-H "Referer: https://bi.vectornode.ru/superset/dashboard/vectornode-anomalies/?native_filters_key=on3j7Uo8xSs"'
)
out = co.read().decode(errors='replace')
print('\nChart POST:')
if 'year = 2024' in out or 'year IN' in out:
    print('  FILTER ACTIVE - year filter in query')
    idx = out.index('"query"')
    print('  ' + out[idx:idx+250])
elif 'HTTP_200' in out:
    print('  200 OK - checking for filter...')
    if '"query"' in out:
        idx = out.index('"query"')
        print('  ' + out[idx:idx+200])
    else:
        print('  No query in response')
elif 'HTTP_302' in out:
    print('  302 Redirect - middleware fallback (no filter or no query_context)')
else:
    print(f'  {out[:300]}')

ssh.close()
