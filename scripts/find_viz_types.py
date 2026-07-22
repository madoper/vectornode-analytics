import paramiko, json

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

def run(cmd):
    stdin, stdout, stderr = ssh.exec_command(cmd)
    return stdout.read().decode(errors='replace').strip()

# Check available viz types in this Superset version
stdin, stdout, stderr = ssh.exec_command(
    "docker exec podft-superset sh -c 'grep -rn \"viz_type\\|VIZ_TYPES\\|get_viz_type\" /app/superset/api/chart/schemas.py 2>/dev/null | head -20'"
)
print('Viz schemas:')
print(stdout.read().decode(errors='replace').strip()[:500])

# Check the viz types directory
stdin2, stdout2, stderr2 = ssh.exec_command(
    "docker exec podft-superset sh -c 'ls /app/.venv/lib/python3.10/site-packages/superset/viz/ 2>/dev/null | head -30'"
)
print('\nViz dirs:')
print(stdout2.read().decode(errors='replace').strip()[:500])

# Check if viz_type has enum/choices
stdin3, stdout3, stderr3 = ssh.exec_command(
    "docker exec podft-superset sh -c 'grep -rn \"viz_type.*Enum\\|VIZ_TYPE\\|viz_types\" /app/superset/models/slice.py 2>/dev/null | head -5'"
)
print('\nSlice model:')
print(stdout3.read().decode(errors='replace').strip()[:500])

# Also check bootstrap data for available viz types
login_resp = run(
    'curl -s -X POST http://127.0.0.1:8088/api/v1/security/login '
    '-H "Content-Type: application/json" '
    '-d \'{"username":"admin","password":"admin","provider":"db"}\''
)
token = json.loads(login_resp)["access_token"]

# Check available viz types via API
stdin4, stdout4, stderr4 = ssh.exec_command(
    f'curl -s -H "Authorization: Bearer {token}" http://127.0.0.1:8088/api/v1/chart/ -d \'{{"page_size": 1}}\' 2>&1'
)
print('\nAPI caps:')
print(stdout4.read().decode(errors='replace').strip()[:500])

# Check explore form data to see available viz types
stdin5, stdout5, stderr5 = ssh.exec_command(
    f'curl -s -H "Authorization: Bearer {token}" "http://127.0.0.1:8088/api/v1/explore/?dataset_id=3&datasource_id=3&datasource_type=table&viz_type=table" 2>&1 | head -20'
)
print('\nExplore:')
print(stdout5.read().decode(errors='replace').strip()[:500])

ssh.close()
