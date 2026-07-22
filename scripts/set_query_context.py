import paramiko, json, base64

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

def run(cmd):
    stdin, stdout, stderr = ssh.exec_command(cmd)
    return stdout.read().decode(errors='replace').strip()

# Check if query_context is null for our charts
stdin, stdout, stderr = ssh.exec_command(
    "docker exec podft-postgres psql -U podft -d superset -c "
    "'SELECT id, slice_name, query_context IS NULL AS qc_null FROM slices ORDER BY id' 2>&1"
)
print('Query context check:')
print(stdout.read().decode(errors='replace').strip()[:600])

# Generate query_context for each chart
# This is a JSON string that includes datasource info
# The format should match what QueryContextFactory.create() expects

charts_qc = {
    1: {
        "datasource": {"id": 3, "type": "table"},
        "queries": [{
            "groupby": ["criticality"],
            "metrics": [{"expressionType": "SIMPLE", "aggregate": "COUNT", "column": {"column_name": "company_id"}, "label": "COUNT(company_id)"}],
            "row_limit": 1000
        }],
        "result_format": "json", "result_type": "full",
        "form_data": {"datasource": "3__table", "groupby": ["criticality"], "metrics": [{"expressionType": "SIMPLE", "aggregate": "COUNT", "column": {"column_name": "company_id"}}], "viz_type": "bar_chart", "row_limit": 1000}
    },
    2: {
        "datasource": {"id": 3, "type": "table"},
        "queries": [{
            "groupby": ["interpretation"],
            "metrics": [{"expressionType": "SIMPLE", "aggregate": "COUNT", "column": {"column_name": "company_id"}, "label": "COUNT(company_id)"}],
            "row_limit": 1000
        }],
        "result_format": "json", "result_type": "full",
        "form_data": {"datasource": "3__table", "groupby": ["interpretation"], "metrics": [{"expressionType": "SIMPLE", "aggregate": "COUNT", "column": {"column_name": "company_id"}}], "viz_type": "pie", "row_limit": 1000}
    },
    3: {
        "datasource": {"id": 3, "type": "table"},
        "queries": [{
            "groupby": ["hypothesis_code"],
            "metrics": [{"expressionType": "SIMPLE", "aggregate": "COUNT", "column": {"column_name": "company_id"}, "label": "COUNT(company_id)"}],
            "row_limit": 1000
        }],
        "result_format": "json", "result_type": "full",
        "form_data": {"datasource": "3__table", "groupby": ["hypothesis_code"], "metrics": [{"expressionType": "SIMPLE", "aggregate": "COUNT", "column": {"column_name": "company_id"}}], "viz_type": "bar_chart", "row_limit": 1000}
    },
    4: {
        "datasource": {"id": 3, "type": "table"},
        "queries": [{
            "columns": ["company_id", "year", "hypothesis_code", "interpretation", "criticality", "criticality_score"],
            "row_limit": 1000
        }],
        "result_format": "json", "result_type": "full",
        "form_data": {"datasource": "3__table", "columns": ["company_id", "year", "hypothesis_code", "interpretation", "criticality", "criticality_score"], "viz_type": "table", "row_limit": 1000}
    },
    5: {
        "datasource": {"id": 3, "type": "table"},
        "queries": [{
            "groupby": ["criticality"],
            "metrics": [{"expressionType": "SIMPLE", "aggregate": "COUNT", "column": {"column_name": "company_id"}, "label": "COUNT(company_id)"}],
            "row_limit": 1000
        }],
        "result_format": "json", "result_type": "full",
        "form_data": {"datasource": "3__table", "groupby": ["criticality"], "metrics": [{"expressionType": "SIMPLE", "aggregate": "COUNT", "column": {"column_name": "company_id"}}], "viz_type": "bar_chart", "row_limit": 1000}
    }
}

for cid, qc in charts_qc.items():
    qc_str = json.dumps(qc).replace("'", "''")
    sql = f"UPDATE slices SET query_context = '{qc_str}' WHERE id = {cid}"
    sql_b64 = base64.b64encode(sql.encode()).decode()
    stdin, stdout, stderr = ssh.exec_command(
        f'echo {sql_b64} | base64 -d | docker exec -i podft-postgres psql -U podft -d superset 2>&1'
    )
    print(f'Chart {cid}: {stdout.read().decode(errors="replace").strip()[:100]}')

# Verify
stdin2, stdout2, stderr2 = ssh.exec_command(
    "docker exec podft-postgres psql -U podft -d superset -c "
    "'SELECT id, slice_name, query_context IS NOT NULL AS has_qc FROM slices ORDER BY id' 2>&1"
)
print('\nVerification:')
print(stdout2.read().decode(errors='replace').strip()[:600])

# Test the GET endpoint
login_resp = run(
    'curl -s -X POST http://127.0.0.1:8088/api/v1/security/login '
    '-H "Content-Type: application/json" '
    '-d \'{"username":"admin","password":"admin","provider":"db"}\''
)
token = json.loads(login_resp)["access_token"]

# Test GET /api/v1/chart/1/data/ 
result = run(
    f'curl -s -i http://127.0.0.1:8088/api/v1/chart/1/data/ '
    f'-H "Authorization: Bearer {token}" 2>&1 | head -25'
)
print(f'\nGET data test: {result[:600]}')

# Test POST with just form_data (should still work for SPA)
form_data = json.dumps({"slice_id": 1})
result2 = run(
    f'curl -s -i -X POST http://127.0.0.1:8088/api/v1/chart/data '
    f'-H "Authorization: Bearer {token}" '
    f'-H "Content-Type: application/json" '
    f'-H "Accept: application/json" '
    f'-d \'{{"form_data": "{form_data}"}}\' 2>&1 | head -25'
)
print(f'\nPOST data test: {result2[:600]}')

ssh.close()
