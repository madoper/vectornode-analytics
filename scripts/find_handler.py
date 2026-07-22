import paramiko, json, base64

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

def run(cmd):
    stdin, stdout, stderr = ssh.exec_command(cmd)
    return stdout.read().decode(errors='replace').strip()

# Check what charts exist
stdin, stdout, stderr = ssh.exec_command(
    "docker exec podft-postgres psql -U podft -d superset -c "
    "'SELECT id, slice_name, datasource_id, params::text FROM slices ORDER BY id' 2>&1"
)
print(stdout.read().decode(errors='replace').strip()[:1500])

# Find the data endpoint in the Superset source
# Look for the route that handles chart/data
stdin2, stdout2, stderr2 = ssh.exec_command(
    "docker exec podft-superset sh -c 'grep -rn \"chart/data\" /app/superset/ --include=\"*.py\" 2>/dev/null | grep -v \".pyc\" | head -10'"
)
print('\nChart data routes:')
print(stdout2.read().decode(errors='replace').strip()[:500])

# Look for the actual handler function
stdin3, stdout3, stderr3 = ssh.exec_command(
    "docker exec podft-superset sh -c 'grep -rn \"data/\\|chart_data\\|load_explore\" /app/superset/views/ --include=\"*.py\" 2>/dev/null | head -10'"
)
print('\nViews:')
print(stdout3.read().decode(errors='replace').strip()[:500])

ssh.close()
