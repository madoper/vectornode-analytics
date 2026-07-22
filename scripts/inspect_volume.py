import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=10)

V = '/var/lib/docker/volumes/podft_superset_data/_data'

# List ALL files in volume
_, o, _ = ssh.exec_command(f'ls -la {V}/')
print('Volume files:')
print(o.read().decode(errors='replace'))

# Check fix_chart_patch.py content
_, o2, _ = ssh.exec_command(f'cat {V}/fix_chart_patch.py')
print('\nfix_chart_patch.py:')
print(o2.read().decode(errors='replace'))

# Check if there's any .pyc or pycache
_, o3, _ = ssh.exec_command(f'find {V} -name "*.pyc" -o -name "__pycache__" | head -20')
print('\npyc/pycache files:', o3.read().decode(errors='replace') or 'NONE')

# Check fix_chart_api.py
_, o4, _ = ssh.exec_command(f'cat {V}/fix_chart_api.py 2>&1')
print('\nfix_chart_api.py:', o4.read().decode(errors='replace')[:500])

ssh.close()
