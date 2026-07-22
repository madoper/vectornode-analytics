import paramiko, json
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=10)

# Restore chart 4 query_context
qc4 = {
    "datasource": {"id": 3, "type": "table"},
    "queries": [{"columns": ["company_id", "company_name", "year", "hypothesis_code", "interpretation", "criticality", "criticality_score", "interpretation_reason", "metric", "value"], "row_limit": 1000}],
    "result_format": "json",
    "result_type": "full",
    "form_data": {"datasource": "3__table", "columns": ["company_id", "company_name", "year", "hypothesis_code", "interpretation", "criticality", "criticality_score", "interpretation_reason", "metric", "value"], "viz_type": "table", "row_limit": 1000}
}

qc_str = json.dumps(qc4).replace("'", "''")
_, o, _ = ssh.exec_command(
    f'docker exec podft-postgres psql -U podft -d superset -c "UPDATE slices SET query_context = \'{qc_str}\' WHERE id = 4"'
)
print(o.read().decode(errors='replace'))

# Verify
_, o2, _ = ssh.exec_command(
    "docker exec podft-postgres psql -U podft -d superset -c \"SELECT id, viz_type, query_context IS NOT NULL AS has_qc FROM slices ORDER BY id\""
)
print(o2.read().decode(errors='replace'))

# Test chart 4 data endpoint
_, out_auth, _ = ssh.exec_command(
    "curl -s -X POST http://127.0.0.1:8088/api/v1/security/login -H 'Content-Type: application/json' -d '{\"username\":\"admin\",\"password\":\"admin\",\"provider\":\"db\"}'"
)
token = json.loads(out_auth.read().decode())["access_token"]

_, out4, _ = ssh.exec_command(
    f'curl -s "http://127.0.0.1:8088/api/v1/chart/4/data/" -H "Authorization: Bearer {token}"'
)
resp = json.loads(out4.read().decode())
result = resp.get("result", [{}])[0]
print(f'\nChart 4: error={result.get("error")}, data_count={len(result.get("data", []))}')

ssh.close()
