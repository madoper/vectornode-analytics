import paramiko, json, base64

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

# Check available viz types by looking at the viz registry
stdin, stdout, stderr = ssh.exec_command(
    "docker exec podft-superset python3 -c \"from superset.viz import viz_types; print(list(viz_types.keys())[:30])\" 2>&1"
)
result = stdout.read().decode(errors='replace').strip()
print('Viz types:', result[:800])

# If python is not available, try with python
if 'python3' not in result:
    stdin2, stdout2, stderr2 = ssh.exec_command(
        "docker exec podft-superset python -c \"from superset.viz import viz_types; print(list(viz_types.keys())[:30])\" 2>&1"
    )
    print('Python viz:', stdout2.read().decode(errors='replace').strip()[:800])

# Also check with docker exec -i
if not result or 'error' in result.lower():
    stdin3, stdout3, stderr3 = ssh.exec_command(
        "docker exec podft-superset /app/.venv/bin/python -c \"from superset.viz import viz_types; print(sorted(viz_types.keys()))\" 2>&1"
    )
    print('\nVenv python:', stdout3.read().decode(errors='replace').strip()[:800])

ssh.close()
