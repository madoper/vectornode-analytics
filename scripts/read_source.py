import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

# Read the full QueryContextFactory.create method
stdin, stdout, stderr = ssh.exec_command(
    "docker exec podft-superset cat /app/superset/common/query_context_factory.py 2>/dev/null"
)
print('QueryContextFactory:')
print(stdout.read().decode(errors='replace').strip()[:2000])

# Read query_context.py to see ChartData endpoint
stdin2, stdout2, stderr2 = ssh.exec_command(
    "docker exec podft-superset grep -n 'def create\\|def load_chart_data\\|def chart_data\\|datasource' /app/superset/common/query_context.py 2>/dev/null | head -20"
)
print('\nQueryContext defs:')
print(stdout2.read().decode(errors='replace').strip()[:500])

# Check how Superset routes handle chart data
stdin3, stdout3, stderr3 = ssh.exec_command(
    "docker exec podft-superset sh -c 'grep -rn \"chart.data\\|ChartData\\|chart/data\" /app/superset/charts/ /app/superset/explore/ /app/superset/api/ 2>/dev/null | head -15'"
)
print('\nChart data in subdirs:')
print(stdout3.read().decode(errors='replace').strip()[:500])

ssh.close()
