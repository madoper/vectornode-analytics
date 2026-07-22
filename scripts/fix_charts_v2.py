import paramiko, json, base64

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

chart_updates = [
    (1, "bar_chart", {"metrics": [{"expressionType": "SIMPLE", "aggregate": "COUNT", "column": {"column_name": "company_id"}, "label": "COUNT(company_id)"}], "groupby": ["criticality"], "time_range": "No filter", "row_limit": 50, "datasource": "3__table"}),
    (2, "pie", {"metrics": [{"expressionType": "SIMPLE", "aggregate": "COUNT", "column": {"column_name": "company_id"}, "label": "COUNT(company_id)"}], "groupby": ["interpretation"], "time_range": "No filter", "datasource": "3__table"}),
    (3, "bar_chart", {"metrics": [{"expressionType": "SIMPLE", "aggregate": "COUNT", "column": {"column_name": "company_id"}, "label": "COUNT(company_id)"}], "groupby": ["hypothesis_code"], "time_range": "No filter", "row_limit": 50, "datasource": "3__table"}),
    (4, "table", {"all_columns": ["company_id", "year", "hypothesis_code", "interpretation", "criticality", "criticality_score", "interpretation_reason"], "time_range": "No filter", "row_limit": 100, "datasource": "3__table"}),
]

for cid, viz, params in chart_updates:
    params_str = json.dumps(params)
    sql = f"UPDATE slices SET params = '{params_str}', viz_type = '{viz}' WHERE id = {cid};"
    sql_b64 = base64.b64encode(sql.encode()).decode()
    stdin, stdout, stderr = ssh.exec_command(
        f'echo {sql_b64} | base64 -d | docker exec -i podft-postgres psql -U podft -d superset 2>&1'
    )
    print(f'Chart {cid}: {stdout.read().decode(errors="replace").strip()[:100]}')

# Verify
stdin2, stdout2, stderr2 = ssh.exec_command(
    "docker exec podft-postgres psql -U podft -d superset -c \"SELECT id, slice_name, params::text FROM slices WHERE id IN (1,2,3,4)\" 2>&1"
)
print('\nParams:')
print(stdout2.read().decode(errors='replace').strip()[:1000])

ssh.close()
