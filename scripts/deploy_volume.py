import paramiko, time
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=10)

# Write directly to Docker volume on host
VOLUME_PATH = '/var/lib/docker/volumes/podft_superset_data/_data'

with open(r'D:\project\FRS_TEST\scripts\fix_chart_patch.py', 'r') as src:
    content = src.read()

# Write to host volume
sftp = ssh.open_sftp()
f = sftp.file(f'{VOLUME_PATH}/fix_chart_patch.py', 'w')
f.write(content)
f.close()
sftp.close()
print('Written to host volume')

# Also write to superset-init for reference
sftp2 = ssh.open_sftp()
f2 = sftp2.file('/opt/podft/infra/superset-init/fix_chart_patch.py', 'w')
f2.write(content)
f2.close()
sftp2.close()
print('Written to superset-init')

# Verify
_, o, _ = ssh.exec_command(f'docker exec podft-superset cat /app/pythonpath/fix_chart_patch.py')
file_content = o.read().decode(errors='replace')
print('\nContent in container:')
print(file_content[:200])

# Check for _patch
if '_patch()' in file_content:
    print('\nERROR: Still has _patch()!')
elif 'patched!' in file_content:
    print('\nOK: Correct content!')
else:
    print('\nWARNING: Unknown content')

# Restart Superset
_, o2, _ = ssh.exec_command('docker restart podft-superset')
print('\nRestarting...')
time.sleep(15)

# Check logs for patched message
_, o3, _ = ssh.exec_command(
    'docker logs podft-superset 2>&1 | grep -i "patched\|NameError" | tail -5'
)
print('\nPatch logs after restart:')
logs = o3.read().decode(errors='replace')
print(logs)

if 'patched' in logs and 'NameError' not in logs:
    print('\nPATCH IS WORKING!')
else:
    print('\nPatch still broken')

ssh.close()
