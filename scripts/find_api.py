import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

# Find the chart data API endpoint definition
stdin, stdout, stderr = ssh.exec_command(
    'docker exec podft-superset grep -rn "chart/data" /app/superset/ --include="*.py" 2>/dev/null | head -10'
)
print('Chart data endpoint:')
print(stdout.read().decode(errors='replace').strip()[:500])

# Also look for QueryContextFactory
stdin2, stdout2, stderr2 = ssh.exec_command(
    'docker exec podft-superset grep -rn "QueryContextFactory" /app/superset/ --include="*.py" 2>/dev/null | head -5'
)
print('\nQueryContextFactory:')
print(stdout2.read().decode(errors='replace').strip()[:500])

ssh.close()
