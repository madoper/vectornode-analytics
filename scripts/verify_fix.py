import paramiko, time, json, urllib.parse
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', port=22, username='root', password='8884&JKL%f75', timeout=15)

# Wait for Superset to fully start
time.sleep(20)

# Check status
_, so, _ = ssh.exec_command('docker ps --filter name=podft-superset --format "{{.Status}}"')
print('Status:', so.read().decode(errors='replace').strip())

# Check the actual volume content
_, so2, _ = ssh.exec_command('cat /var/lib/docker/volumes/podft_superset_data/_data/superset_config.py')
vol_conf = so2.read().decode(errors='replace')
print('Volume config size:', len(vol_conf), 'bytes')

# Check host config
_, so3, _ = ssh.exec_command('wc -l /opt/podft/infra/superset-init/superset_config.py')
print('Host config lines:', so3.read().decode(errors='replace').strip())

# Check inside container
_, so4, _ = ssh.exec_command('docker exec podft-superset wc -l /app/pythonpath/superset_config.py 2>&1')
print('Container config:', so4.read().decode(errors='replace').strip())

# If empty, copy host config to volume
if len(vol_conf.strip()) < 50:
    print('\nVolume config broken! Copying host config...')
    _, so5, _ = ssh.exec_command(
        'cp /opt/podft/infra/superset-init/superset_config.py /var/lib/docker/volumes/podft_superset_data/_data/superset_config.py'
    )
    print('Copied:', so5.read().decode(errors='replace').strip())
    
    # Restart
    _, so6, _ = ssh.exec_command('docker restart podft-superset')
    print('Restarting...')
    time.sleep(25)

# Check for errors
_, so7, _ = ssh.exec_command(
    'docker logs podft-superset --since 30s 2>&1 | grep -i "syntax\\|error\\|traceback" | tail -3'
)
print('\nRecent errors:', so7.read().decode(errors='replace').strip() or 'NONE')

# Test login
time.sleep(10)
for attempt in range(3):
    _, auth, _ = ssh.exec_command(
        'curl -s -X POST http://127.0.0.1:8088/api/v1/security/login -H "Content-Type: application/json" -d \'{"username":"admin","password":"admin","provider":"db"}\''
    )
    resp = auth.read().decode(errors='replace')
    if resp.startswith('{') and 'access_token' in resp:
        token = json.loads(resp)["access_token"]
        print('\nLogin OK!')
        
        # Test chart POST
        fd = urllib.parse.quote('{"slice_id":5}')
        _, co, _ = ssh.exec_command(
            'curl -s -w "\nHTTP_%{http_code}" -X POST "http://127.0.0.1:8088/api/v1/chart/data?form_data=' + fd + '" '
            '-H "Authorization: Bearer ' + token + '" '
            '-H "Content-Type: application/json"'
        )
        print('Chart POST:', co.read().decode(errors='replace')[:400])
        
        # Test native filter
        _, co2, _ = ssh.exec_command(
            'curl -s -w "\nHTTP_%{http_code}" -X POST http://127.0.0.1:8088/api/v1/chart/data '
            '-H "Content-Type: application/json" '
            '-H "Authorization: Bearer ' + token + '" '
            '-d \'{"datasource":{"id":3,"type":"table"},"queries":[{"columns":["year"],"row_limit":5}]}\''
        )
        print('\nNative filter POST:', co2.read().decode(errors='replace')[:300])
        break
    else:
        print(f'Login attempt {attempt+1} failed:', resp[:80])
        time.sleep(10)

# Get version
_, so8, _ = ssh.exec_command('docker exec podft-superset python3 -c "import superset; print(superset.__version__)" 2>/dev/null || echo VERSION_UNKNOWN')
print('\nVersion:', so8.read().decode(errors='replace').strip())

ssh.close()
