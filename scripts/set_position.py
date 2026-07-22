import paramiko, json

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

# Set dashboard position_json for proper layout
position = {
    "DASHBOARD_VERSION": "v2",
    "ROOT_ID": {"type": "ROOT", "id": "ROOT_ID", "children": ["GRID_ID"]},
    "GRID_ID": {"type": "GRID", "id": "GRID_ID", "children": ["CHART-1", "CHART-2", "CHART-3", "CHART-4"]},
    "HEADER_ID": {"type": "HEADER", "id": "HEADER_ID", "meta": {"text": "VectorNode Analytics"}},
    "CHART-1": {"type": "CHART", "id": "CHART-1", "children": [], "meta": {"chartId": 1, "height": 50, "width": 6, "sliceName": "Criticality Distribution"}, "parents": ["ROOT_ID", "GRID_ID"]},
    "CHART-2": {"type": "CHART", "id": "CHART-2", "children": [], "meta": {"chartId": 2, "height": 50, "width": 6, "sliceName": "Interpretation Breakdown"}, "parents": ["ROOT_ID", "GRID_ID"]},
    "CHART-3": {"type": "CHART", "id": "CHART-3", "children": [], "meta": {"chartId": 3, "height": 50, "width": 6, "sliceName": "Hypothesis Distribution"}, "parents": ["ROOT_ID", "GRID_ID"]},
    "CHART-4": {"type": "CHART", "id": "CHART-4", "children": [], "meta": {"chartId": 4, "height": 50, "width": 12, "sliceName": "Anomalies Table"}, "parents": ["ROOT_ID", "GRID_ID"]}
}

position_json = json.dumps(position).replace("'", "''")
cmd = f"docker exec podft-postgres psql -U podft -d superset -c \"UPDATE dashboards SET position_json = '{position_json}' WHERE id=2\" 2>&1"
stdin, stdout, stderr = ssh.exec_command(cmd)
print('Position:', stdout.read().decode(errors='replace').strip()[:100])

# Verify
stdin2, stdout2, stderr2 = ssh.exec_command("docker exec podft-postgres psql -U podft -d superset -c \"SELECT dashboard_title, slug FROM dashboards WHERE id=2\" 2>&1")
print('Dashboard:', stdout2.read().decode(errors='replace').strip())

ssh.close()
