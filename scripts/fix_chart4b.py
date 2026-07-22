import paramiko, json, subprocess
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=10)

# Chart 4 query_context
qc4 = {
    "datasource": {"id": 3, "type": "table"},
    "queries": [{"columns": ["company_id", "company_name", "year", "hypothesis_code", "interpretation", "criticality", "criticality_score", "interpretation_reason", "metric", "value"], "row_limit": 1000}],
    "result_format": "json",
    "result_type": "full",
    "form_data": {"datasource": "3__table", "columns": ["company_id", "company_name", "year", "hypothesis_code", "interpretation", "criticality", "criticality_score", "interpretation_reason", "metric", "value"], "viz_type": "table", "row_limit": 1000}
}

# Base64 encode
import base64
encoded = base64.b64encode(json.dumps(qc4).encode()).decode()

# Write and decode on server, then update
cmd = f'echo {encoded} | base64 -d | docker exec -i podft-postgres psql -U podft -d superset -c "UPDATE slices SET query_context = pg_read_file(\'/dev/stdin\')"'
# Actually pg_read_file doesn't work that way. Let me use a different approach.

# Write query_context to a temp file on server, then use psql
sftp = ssh.open_sftp()
f = sftp.file('/tmp/qc4.json', 'w')
f.write(json.dumps(qc4))
f.close()
sftp.close()

# Now update using the file
_, o, _ = ssh.exec_command(
    "docker cp /tmp/qc4.json podft-postgres:/tmp/qc4.json"
)
print("cp:", o.read().decode(errors='replace'))

# Read the file into a variable and update
_, o2, _ = ssh.exec_command(
    "docker exec podft-postgres psql -U podft -d superset -c \"UPDATE slices SET query_context = pg_read_file('/tmp/qc4.json') WHERE id = 4\""
)
print("update:", o2.read().decode(errors='replace'))

# Verify
_, o3, _ = ssh.exec_command(
    "docker exec podft-postgres psql -U podft -d superset -c \"SELECT id, viz_type, LEFT(query_context, 100) FROM slices WHERE id = 4\""
)
print("verify:", o3.read().decode(errors='replace'))

# Cleanup
_, o4, _ = ssh.exec_command("rm /tmp/qc4.json")

ssh.close()
