import paramiko, time
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=10)

VOLUME_PATH = '/var/lib/docker/volumes/podft_superset_data/_data'

# Check current file
_, o, _ = ssh.exec_command(f'cat {VOLUME_PATH}/fix_chart_patch.py')
print('Current file content:')
content = o.read().decode(errors='replace')
print(content)

# Check for .create in file
if '.create' in content:
    print('\nERROR: Still has .create!')
else:
    print('\nOK: No .create in file')

# Check for stale pyc
_, o2, _ = ssh.exec_command(f'ls -la {VOLUME_PATH}/__pycache__/ 2>/dev/null || echo "no pycache"')
print('\nPycache:', o2.read().decode(errors='replace')[:500])

# Also check inside container
_, o3, _ = ssh.exec_command('docker exec podft-superset cat /app/pythonpath/fix_chart_patch.py')
print('\nContainer file:')
print(o3.read().decode(errors='replace'))

# Aggressive: stop container, delete pycache, delete file, write fresh, start
_, o4, _ = ssh.exec_command('docker stop podft-superset')
print('\nStopped:', o4.read().decode(errors='replace').strip())

# Delete all .pyc and pycache
_, o5, _ = ssh.exec_command(f'find {VOLUME_PATH} -name "*.pyc" -delete 2>/dev/null; find {VOLUME_PATH} -name "__pycache__" -type d -exec rm -rf {{}} + 2>/dev/null; echo "Cleaned"')
print('Cleaned:', o5.read().decode(errors='replace').strip())

# Write fresh patch file
with open(r'D:\project\FRS_TEST\scripts\fix_chart_patch.py', 'r') as src:
    new_content = src.read()

sftp = ssh.open_sftp()
f = sftp.file(f'{VOLUME_PATH}/fix_chart_patch.py', 'w')
f.write(new_content)
f.close()
sftp.close()

# Also delete the old fix_chart_api.py just in case
_, o6, _ = ssh.exec_command(f'rm -f {VOLUME_PATH}/fix_chart_api.py*; echo "Removed old files"')
print('Removed:', o6.read().decode(errors='replace').strip())

# Verify write
_, o7, _ = ssh.exec_command(f'cat {VOLUME_PATH}/fix_chart_patch.py')
vf = o7.read().decode(errors='replace')
print('\nVerified write, has .create:', '.create' in vf)

# Start container
_, o8, _ = ssh.exec_command('docker start podft-superset')
print('Started:', o8.read().decode(errors='replace').strip())

time.sleep(20)

# Check logs
_, o9, _ = ssh.exec_command(
    'docker logs podft-superset 2>&1 | grep -E "patched|Error|Traceback" | tail -10'
)
print('\nFinal logs:')
print(o9.read().decode(errors='replace'))

ssh.close()
