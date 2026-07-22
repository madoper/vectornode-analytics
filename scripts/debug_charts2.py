import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=10)

# View columns
_, o, _ = ssh.exec_command(
    "docker exec podft-postgres psql -U podft -d analytics -c \"SELECT column_name, data_type FROM information_schema.columns WHERE table_schema='analytics' AND table_name='v_company_dashboard' ORDER BY ordinal_position\""
)
print('=== VIEW COLUMNS ===')
print(o.read().decode(errors='replace'))

# Full query_context for chart 2 (Interpretation breakdown)
_, o2, _ = ssh.exec_command(
    "docker exec podft-postgres psql -U podft -d superset -c \"SELECT query_context FROM slices WHERE id=2\""
)
print('=== CHART 2 FULL QC ===')
print(o2.read().decode(errors='replace'))

# Full query_context for chart 3
_, o3, _ = ssh.exec_command(
    "docker exec podft-postgres psql -U podft -d superset -c \"SELECT query_context FROM slices WHERE id=3\""
)
print('=== CHART 3 FULL QC ===')
print(o3.read().decode(errors='replace'))

# Full query_context for chart 4
_, o4, _ = ssh.exec_command(
    "docker exec podft-postgres psql -U podft -d superset -c \"SELECT query_context FROM slices WHERE id=4\""
)
print('=== CHART 4 FULL QC ===')
print(o4.read().decode(errors='replace'))

# Check the actual query being generated - test via API
import json
_, out_auth, _ = ssh.exec_command(
    "curl -s -X POST http://127.0.0.1:8088/api/v1/security/login -H 'Content-Type: application/json' -d '{\"username\":\"admin\",\"password\":\"admin\",\"provider\":\"db\"}'"
)
token = json.loads(out_auth.read().decode())["access_token"]

for cid in [2, 3, 4]:
    _, out, _ = ssh.exec_command(
        f'curl -s "http://127.0.0.1:8088/api/v1/chart/{cid}/data/" -H "Authorization: Bearer {token}"'
    )
    resp = json.loads(out.read().decode())
    result = resp.get("result", [{}])[0]
    print(f'\n=== Chart {cid} result ===')
    print(f'  error: {result.get("error")}')
    print(f'  query: {result.get("query","")[:300]}')
    print(f'  data_count: {len(result.get("data", []))}')
    if result.get("data"):
        print(f'  data[0]: {list(result["data"][0].keys()) if result["data"] else "empty"}')

ssh.close()
