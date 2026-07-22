import urllib.request, json

TOKEN = ""  # overridden by login API below

def api(path, method="GET", data=None):
    url = f"http://127.0.0.1:8088/api/v1/{path}"
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json",
        "User-Agent": "python"
    }
    req = urllib.request.Request(url, headers=headers, method=method)
    if data:
        req.data = json.dumps(data).encode()
    resp = urllib.request.urlopen(req)
    return json.loads(resp.read())

# Login
login = api("security/login", "POST", {"username": "admin", "password": "admin", "provider": "db"})
TOKEN = login["access_token"]
print(f"Token: {TOKEN[:20]}...")

# Get CSRF token
csrf = api("security/csrf_token/")
csrf_token = csrf["result"]
print(f"CSRF: {csrf_token[:20]}...")

# Get dataset columns
ds = api("dataset/3")
print(f"Datasets columns: {len(ds.get('result', {}).get('columns', []))}")

ssh.close()

# Update chart 1: Criticality distribution - better params
chart1_params = {
    "metrics": [{"expressionType": "SIMPLE", "aggregate": "COUNT", "column": {"column_name": "company_id"}, "label": "COUNT(company_id)"}],
    "groupby": ["criticality"],
    "time_range": "No filter",
    "order_desc": True,
    "row_limit": 100
}

# Update chart 2: Interpretation breakdown
chart2_params = {
    "metrics": [{"expressionType": "SIMPLE", "aggregate": "COUNT", "column": {"column_name": "company_id"}, "label": "COUNT(company_id)"}],
    "groupby": ["interpretation"],
    "time_range": "No filter"
}

# Update chart 3: Hypothesis distribution
chart3_params = {
    "metrics": [{"expressionType": "SIMPLE", "aggregate": "COUNT", "column": {"column_name": "company_id"}, "label": "COUNT(company_id)"}],
    "groupby": ["hypothesis_code"],
    "time_range": "No filter",
    "row_limit": 100
}

# Update chart 4: Anomalies table
chart4_params = {
    "all_columns": ["company_id", "year", "hypothesis_code", "interpretation", "criticality", "criticality_score", "interpretation_reason"],
    "time_range": "No filter",
    "row_limit": 100,
    "order_desc": True
}

charts = [
    (1, "bar_chart", chart1_params),
    (2, "pie", chart2_params),
    (3, "bar_chart", chart3_params),
    (4, "table", chart4_params),
]

for chart_id, viz_type, params in charts:
    payload = {
        "slice_name": f"Chart {chart_id}",
        "viz_type": viz_type,
        "datasource_id": 3,
        "datasource_type": "table",
        "params": json.dumps(params)
    }
    update = api(f"chart/{chart_id}", "PUT", payload)
    print(f"Chart {chart_id} updated: {update.get('result', {}).get('slice_name', 'error')}")

print("Charts updated")
