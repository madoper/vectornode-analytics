import paramiko, time
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=10)

# Upload fixed patch
sftp = ssh.open_sftp()
sftp.put(r'D:\project\FRS_TEST\scripts\fix_chart_patch.py', '/opt/podft/infra/superset-init/fix_chart_patch.py')
sftp.close()
print('Patch uploaded')

# Restart Superset
_, o, _ = ssh.exec_command('docker restart podft-superset 2>&1')
print('Restart:', o.read().decode(errors='replace'))

# Wait and check logs
time.sleep(10)
_, o2, _ = ssh.exec_command('docker logs podft-superset --tail 20 2>&1')
logs = o2.read().decode(errors='replace')
print('Logs:')
print(logs[-500:])

# Check for the patched message
if 'ChartDataRestApi patched' in logs:
    print('\nPATCH WORKING!')
else:
    print('\nPatch message not found in logs, checking if service is up...')
    _, o3, _ = ssh.exec_command('docker logs podft-superset 2>&1 | grep -i "patched\|patch\|error" | tail -10')
    print(o3.read().decode(errors='replace'))

ssh.close()
