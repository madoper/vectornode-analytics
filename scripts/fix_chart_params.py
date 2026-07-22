import paramiko, json, base64

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

# Update chart params to include datasource properly
for chart_id, name, viz, params in [
    (1, "Criticality Distribution", "bar_chart", {
        "metrics": [{"expressionType": "SIMPLE", "aggregate": "COUNT", "column": {"column_name": "company_id"}, "label": "COUNT(company_id)"}],
        "groupby": ["criticality"], "time_range": "No filter", "row_limit": 50,
        "datasource": "3__table", "granularity_sqla": "year"
    }),
    (2, "Interpretation Breakdown", "pie", {
        "metrics": [{"expressionType": "SIMPLE", "aggregate": "COUNT", "column": {"column_name": "company_id"}, "label": "COUNT(company_id)"}],
        "groupby": ["interpretation"], "time_range": "No filter",
        "datasource": "3__table"
    }),
    (3, "Hypothesis Distribution", "bar_chart", {
        "metrics": [{"expressionType": "SIMPLE", "aggregate": "COUNT", "column": {"column_name": "company_id"}, "label": "COUNT(company_id)"}],
        "groupby": ["hypothesis_code"], "time_range": "No filter", "row_limit": 50,
        "datasource": "3__table", "granularity_sqla": "year"
    }),
    (4, "Anomalies Table", "table", {
        "all_columns": ["company_id", "year", "hypothesis_code", "interpretation", "criticality", "criticality_score", "interpretation_reason"],
        "time_range": "No filter", "row_limit": 100,
        "datasource": "3__table"
    }),
]:
    params_json = json.dumps(params).replace("'", "''")
    sql = f"UPDATE slices SET params = '{params_json}', viz_type = '{viz}' WHERE id = {chart_id}"
    stdin, stdout, stderr = ssh.exec_command(
        f'docker exec podft-postgres psql -U podft -d superset -c "{sql}" 2>&1'
    )
    print(f'Chart {chart_id} ({name}): {stdout.read().decode(errors="replace").strip()[:100]}')

# Now test the chart data API
stdin2, stdout2, stderr2 = ssh.exec_command(
    'docker exec podft-postgres psql -U podft -d superset -c "SELECT id, slice_name, params::text FROM slices WHERE id IN (1,2,3,4)" 2>&1'
)
print('\nUpdated params:')
print(stdout2.read().decode(errors='replace').strip()[:800])

ssh.close()
