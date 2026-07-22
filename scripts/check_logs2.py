import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=10)

# Find log files
_, o, _ = ssh.exec_command('find /opt/analytics/logs -name "*.log" -path "*build_group*" 2>/dev/null')
print('Log files:')
print(o.read().decode(errors='replace') or 'None found')

# Also try listing the log directory structure
_, o2, _ = ssh.exec_command('ls -la /opt/analytics/logs/vectornode_anomaly_etl/build_group_signals/ 2>/dev/null || echo "No dir"')
print('\nDir listing:')
print(o2.read().decode(errors='replace'))

# Check the actual log
_, o3, _ = ssh.exec_command('find /opt/analytics/logs -name "*.log" -type f 2>/dev/null | tail -20')
print('\nAll log files:')
print(o3.read().decode(errors='replace') or 'None')

ssh.close()
