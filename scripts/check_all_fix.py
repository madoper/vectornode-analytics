import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=10)

# Check for other fix files
_, o, _ = ssh.exec_command('docker exec podft-superset ls -la /app/pythonpath/fix* 2>&1')
print('All fix files:')
print(o.read().decode(errors='replace'))

# Check fix_chart_api.py
_, o2, _ = ssh.exec_command('docker exec podft-superset cat /app/pythonpath/fix_chart_api.py 2>&1')
print('\nfix_chart_api.py:')
print(o2.read().decode(errors='replace')[:1000])

# Check superset_config.py for imports
_, o3, _ = ssh.exec_command('docker exec podft-superset grep "fix_" /app/pythonpath/superset_config.py 2>&1')
print('\nConfig imports:')
print(o3.read().decode(errors='replace'))

# Check volume path
_, o4, _ = ssh.exec_command('docker volume inspect podft_superset_data --format "{{.Mountpoint}}" 2>&1')
print('\nVolume mount point:')
print(o4.read().decode(errors='replace'))

ssh.close()
