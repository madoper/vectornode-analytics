import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=10)

# Check for old fix files
_, o, _ = ssh.exec_command('docker exec podft-superset ls -la /app/pythonpath/fix* 2>/dev/null')
print('Fix files:')
print(o.read().decode(errors='replace'))

# Check the actual fix_chart_patch.py in container
_, o2, _ = ssh.exec_command('docker exec podft-superset cat /app/pythonpath/fix_chart_patch.py')
print('\nCurrent fix_chart_patch.py:')
print(o2.read().decode(errors='replace'))

# Check full error trace
_, o3, _ = ssh.exec_command(
    'docker logs podft-superset 2>&1 | grep -B5 -A10 "fix_chart\\|Traceback\\|Error\\|patched" | tail -60'
)
print('\n\nFull error logs:')
print(o3.read().decode(errors='replace'))

ssh.close()
