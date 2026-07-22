import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

# Find the data endpoint
stdin, stdout, stderr = ssh.exec_command('docker exec podft-superset sh -c "grep -rn \"chart_data\\|ChartData\\|chart/data\" /app/superset/api/ 2>/dev/null | head -20"')
print('API results:')
print(stdout.read().decode(errors='replace').strip()[:1500])

# Check the main explore/datasource views
stdin2, stdout2, stderr2 = ssh.exec_command('docker exec podft-superset sh -c "grep -rn \"QueryContextFactory.create\\|def chart_data\" /app/superset/views/ 2>/dev/null | head -10"')
print('\nViews:')
print(stdout2.read().decode(errors='replace').strip()[:1500])

ssh.close()
