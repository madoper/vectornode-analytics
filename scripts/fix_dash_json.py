import paramiko, json

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

# Write a Python script on the server that fixes the dashboard JSON
python_script = '''
import json, psycopg2

# Connect to superset database
conn = psycopg2.connect(
    host="localhost", port=5432, user="podft", 
    password="podft-secret", dbname="superset"
)
cur = conn.cursor()

# Proper json_metadata with quoted keys
json_meta = json.dumps({
    "native_filter_configuration": [
        {"id": "NF-year", "filterType": "filter_select", "column": "year", "name": "Year", "multiple": True, "dataset": 3},
        {"id": "NF-region", "filterType": "filter_select", "column": "region", "name": "Region", "multiple": True, "dataset": 3},
        {"id": "NF-okved", "filterType": "filter_select", "column": "okved_section", "name": "Industry", "multiple": True, "dataset": 3},
        {"id": "NF-interp", "filterType": "filter_select", "column": "interpretation", "name": "Interpretation", "multiple": True, "dataset": 3},
        {"id": "NF-crit", "filterType": "filter_select", "column": "criticality", "name": "Criticality", "multiple": True, "dataset": 3},
        {"id": "NF-hypo", "filterType": "filter_select", "column": "hypothesis_code", "name": "Hypothesis", "multiple": True, "dataset": 3}
    ],
    "timed_refresh_immune_slices": [],
    "expanded_slices": {},
    "refresh_frequency": 0,
    "default_filters": "{}"
})

cur.execute("UPDATE dashboards SET json_metadata = %s WHERE id = 2", (json_meta,))
conn.commit()
print("json_metadata updated")

# Reset position_json
position = json.dumps({})
cur.execute("UPDATE dashboards SET position_json = %s WHERE id = 2", (position,))
conn.commit()
print("position_json reset")

cur.close()
conn.close()
'''

# Write to server
sftp = ssh.open_sftp()
with sftp.open('/tmp/fix_dash.py', 'w') as f:
    f.write(python_script.encode())
sftp.close()

# Run via docker exec (since Python is in container)
stdin, stdout, stderr = ssh.exec_command(
    'docker exec -i podft-postgres python3 -c "'
    'import json, psycopg2; '
    'conn = psycopg2.connect(host=\\"localhost\\", port=5432, user=\\"podft\\", password=\\"podft-secret\\", dbname=\\"superset\\"); '
    'cur = conn.cursor(); '
    'cur.execute(\\"UPDATE dashboards SET json_metadata = %s WHERE id = 2\\", (json.dumps({\\"native_filter_configuration\\": []}),)); '
    'conn.commit(); '
    'cur.close(); conn.close(); '
    'print(\\"done\\")" 2>&1'
)
print(stdout.read().decode(errors='replace').strip())

# Simpler approach: write to temp file and use psql
import base64
json_meta = json.dumps({
    "native_filter_configuration": [
        {"id": "NF-year", "filterType": "filter_select", "column": "year", "name": "Year", "multiple": True, "dataset": 3},
        {"id": "NF-region", "filterType": "filter_select", "column": "region", "name": "Region", "multiple": True, "dataset": 3},
        {"id": "NF-okved", "filterType": "filter_select", "column": "okved_section", "name": "Industry", "multiple": True, "dataset": 3},
        {"id": "NF-interp", "filterType": "filter_select", "column": "interpretation", "name": "Interpretation", "multiple": True, "dataset": 3},
        {"id": "NF-crit", "filterType": "filter_select", "column": "criticality", "name": "Criticality", "multiple": True, "dataset": 3},
        {"id": "NF-hypo", "filterType": "filter_select", "column": "hypothesis_code", "name": "Hypothesis", "multiple": True, "dataset": 3}
    ],
    "timed_refresh_immune_slices": [],
    "expanded_slices": {},
    "refresh_frequency": 0,
    "default_filters": "{}"
})

sql = "UPDATE dashboards SET json_metadata = '" + json_meta.replace("'", "''") + "' WHERE id = 2;"
sql_b64 = base64.b64encode(sql.encode()).decode()

stdin2, stdout2, stderr2 = ssh.exec_command(f'echo {sql_b64} | base64 -d | docker exec -i podft-postgres psql -U podft -d superset 2>&1')
print('Update:', stdout2.read().decode(errors='replace').strip())

# Verify
stdin3, stdout3, stderr3 = ssh.exec_command("docker exec podft-postgres psql -U podft -d superset -c \"SELECT json_metadata FROM dashboards WHERE id=2\" -A -t 2>&1")
print('\nVerified:', stdout3.read().decode(errors='replace').strip()[:200])

ssh.close()
