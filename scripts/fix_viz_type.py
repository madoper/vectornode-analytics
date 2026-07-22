import paramiko, json
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=10)

# Fix viz_type for each chart
fixes = {
    1: {"viz_type": "table", "form_data_viz": "table",
        "params": {"datasource": "3__table", "viz_type": "table",
                   "groupby": ["criticality"],
                   "metrics": [{"aggregate": "COUNT", "column": {"column_name": "company_id"},
                                "expressionType": "SIMPLE", "label": "COUNT(company_id)"}],
                   "time_range": "No filter", "row_limit": 1000}},
    2: {"viz_type": "table", "form_data_viz": "table",
        "params": {"datasource": "3__table", "viz_type": "table",
                   "groupby": ["interpretation"],
                   "metrics": [{"aggregate": "COUNT", "column": {"column_name": "company_id"},
                                "expressionType": "SIMPLE", "label": "COUNT(company_id)"}],
                   "time_range": "No filter", "row_limit": 1000}},
    3: {"viz_type": "table", "form_data_viz": "table",
        "params": {"datasource": "3__table", "viz_type": "table",
                   "groupby": ["hypothesis_code"],
                   "metrics": [{"aggregate": "COUNT", "column": {"column_name": "company_id"},
                                "expressionType": "SIMPLE", "label": "COUNT(company_id)"}],
                   "time_range": "No filter", "row_limit": 1000}},
    4: {"viz_type": "table", "form_data_viz": "table",
        "params": {"datasource": "3__table", "viz_type": "table",
                   "all_columns": ["company_id", "company_name", "year", "hypothesis_code",
                                   "interpretation", "criticality", "criticality_score",
                                   "interpretation_reason", "metric", "value"],
                   "time_range": "No filter", "row_limit": 1000}},
    5: {"viz_type": "table", "form_data_viz": "table",
        "params": {"datasource": "3__table", "viz_type": "table",
                   "groupby": ["criticality"],
                   "metrics": [{"aggregate": "COUNT", "column": {"column_name": "company_id"},
                                "expressionType": "SIMPLE", "label": "COUNT(company_id)"}],
                   "time_range": "No filter", "row_limit": 1000}},
}

for cid, fix in fixes.items():
    # Update viz_type
    _, o, _ = ssh.exec_command(
        f"docker exec podft-postgres psql -U podft -d superset -c "
        f"\"UPDATE slices SET viz_type = '{fix['viz_type']}' WHERE id = {cid}\""
    )
    print(f"Chart {cid} viz_type -> {o.read().decode(errors='replace').strip()}")

    # Update query_context form_data.viz_type
    _, o2, _ = ssh.exec_command(
        f"docker exec podft-postgres psql -U podft -d superset -c "
        f"\"SELECT query_context FROM slices WHERE id = {cid}\""
    )
    qc_str = o2.read().decode(errors='replace')
    lines = qc_str.strip().split('\n')
    json_line = None
    for line in lines:
        line = line.strip()
        if line.startswith('{') or line.startswith(' '):
            if '{' in line:
                json_line = line.strip()
                break
    
    if json_line:
        qc = json.loads(json_line)
        if 'form_data' in qc:
            qc['form_data']['viz_type'] = fix['form_data_viz']
        updated_qc = json.dumps(qc)
        # Update
        safe_qc = updated_qc.replace("'", "''")
        _, o3, _ = ssh.exec_command(
            f"docker exec podft-postgres psql -U podft -d superset -c "
            f"\"UPDATE slices SET query_context = '{safe_qc}' WHERE id = {cid}\""
        )
        print(f"  query_context updated")

    # Update params
    params_json = json.dumps(fix["params"])
    safe_params = params_json.replace("'", "''")
    _, o4, _ = ssh.exec_command(
        f"docker exec podft-postgres psql -U podft -d superset -c "
        f"\"UPDATE slices SET params = '{safe_params}' WHERE id = {cid}\""
    )
    print(f"  params updated")

# Verify
_, overify, _ = ssh.exec_command(
    "docker exec podft-postgres psql -U podft -d superset -c "
    "\"SELECT id, slice_name, viz_type FROM slices ORDER BY id\""
)
print('\n=== VERIFIED ===')
print(overify.read().decode(errors='replace'))

ssh.close()
