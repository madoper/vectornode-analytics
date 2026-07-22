import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

# Find the chart data endpoint implementation
cmds = [
    'docker exec podft-superset grep -rn "def chart_data" /app/superset/ --include="*.py" 2>/dev/null | head -5',
    'docker exec podft-superset grep -rn "QueryContextFactory" /app/superset/ --include="*.py" 2>/dev/null | head -10',
    'docker exec podft-superset grep -rn "datasource" /app/superset/models/slice.py 2>/dev/null | head -10',
    'docker exec podft-superset find /app/superset -name "*.py" -exec grep -l "class.*ChartData\|chart.data\|chart_data" {} \; 2>/dev/null | head -5',
]

for cmd in cmds:
    stdin, stdout, stderr = ssh.exec_command(cmd)
    print(f'---')
    print(stdout.read().decode(errors='replace').strip()[:800])

ssh.close()
