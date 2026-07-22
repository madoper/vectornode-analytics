import paramiko, json, time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

# Login
stdin, stdout, stderr = ssh.exec_command(
    "curl -s -X POST http://127.0.0.1:8088/api/v1/security/login "
    "-H 'Content-Type: application/json' "
    "-d '{\"username\":\"admin\",\"password\":\"admin\",\"provider\":\"db\"}'"
)
token = json.loads(stdout.read().decode())["access_token"]

# Get the full 400 error message
fd = json.dumps({"slice_id": 1})
cmd = f"curl -s -X POST 'http://127.0.0.1:8088/api/v1/chart/data?form_data={fd}' -H 'Authorization: Bearer {token}' 2>&1"
stdin2, stdout2, stderr2 = ssh.exec_command(cmd)
resp = stdout2.read().decode(errors='replace').strip()
print(f"Full response: {resp}")

# Also check if the fix module runs by looking at Superset logs
stdin3, stdout3, stderr3 = ssh.exec_command(
    "docker logs podft-superset --tail 20 2>&1 | grep -i 'fix_chart\\|before_request\\|error\\|traceback' | head -5"
)
print(f"\nLogs: {stdout3.read().decode(errors='replace').strip()[:500]}")

# Check what endpoint name the request has - add a debug endpoint
# Actually, let me just check the fix_chart_api module directly
stdin4, stdout4, stderr4 = ssh.exec_command(
    "docker exec podft-superset cat /app/pythonpath/fix_chart_api.py 2>/dev/null"
)
print(f"\nModule content: {stdout4.read().decode(errors='replace').strip()[:500]}")

# Check if module gets imported by checking for errors in config
stdin5, stdout5, stderr5 = ssh.exec_command(
    "docker exec podft-superset sh -c 'python3 -c \"import fix_chart_api; print(\\\"OK\\\")\" 2>&1'"
)
print(f"\nImport test: {stdout5.read().decode(errors='replace').strip()[:200]}")

ssh.close()
