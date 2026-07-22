import paramiko, time, json, urllib.parse
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', port=22, username='root', password='8884&JKL%f75', timeout=15)

V = '/var/lib/docker/volumes/podft_superset_data/_data'
sftp = ssh.open_sftp()
sftp.put(r'D:\project\FRS_TEST\scripts\superset_config_clean.py', '/opt/podft/infra/superset-init/superset_config.py')
sftp.put(r'D:\project\FRS_TEST\scripts\superset_config_clean.py', f'{V}/superset_config.py')
sftp.close()
ssh.exec_command(f'find {V} -name "*.pyc" -delete; find {V} -name "__pycache__" -exec rm -rf {{}} +')

_, so, _ = ssh.exec_command('docker restart podft-superset')
print('Restarting...')
time.sleep(45)

_, auth, _ = ssh.exec_command(
    'curl -s -X POST http://127.0.0.1:8088/api/v1/security/login -H "Content-Type: application/json" -d \'{"username":"admin","password":"admin","provider":"db"}\''
)
resp = auth.read().decode(errors='replace')
token = json.loads(resp)["access_token"]

fd = urllib.parse.quote('{"slice_id":4}')
_, co, _ = ssh.exec_command(
    'curl -s -w "\nHTTP_%{http_code}" -X POST "http://127.0.0.1:8088/api/v1/chart/data?form_data=' + fd + '&dashboard_id=2" '
    '-H "Content-Type: application/json" '
    '-H "Authorization: Bearer ' + token + '" '
    '-H "Referer: https://bi.vectornode.ru/superset/dashboard/vectornode-anomalies/?native_filters_key=on3j7Uo8xSs"'
)
out = co.read().decode(errors='replace')
if 'HTTP_200' in out:
    if 'year = 2024' in out:
        print('SUCCESS! Filter applied (year=2024)!')
    else:
        print('200 but no filter in query')
        if '"query"' in out:
            idx = out.index('"query"')
            print(out[idx:idx+250])
else:
    print('Result:', out[:400])

# Check debug logs
_, so2, _ = ssh.exec_command('docker logs podft-superset --since 1m 2>&1 | grep -E "QC_LOAD|FILTER_|app_context" | tail -5')
print('\nDebug:', so2.read().decode(errors='replace') or 'NONE')

ssh.close()
