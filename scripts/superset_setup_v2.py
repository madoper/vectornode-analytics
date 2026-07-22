import paramiko, json, time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

def run(cmd):
    stdin, stdout, stderr = ssh.exec_command(cmd)
    return stdout.read().decode(errors='replace').strip()

# Login
login = run(
    'curl -s -c /tmp/ss_cookies.txt -X POST http://127.0.0.1:8088/api/v1/security/login '
    '-H "Content-Type: application/json" '
    '-d \'{"username":"admin","password":"admin","provider":"db"}\''
)
token = json.loads(login)["access_token"]
print(f"Token OK")

# Get CSRF
csrf_resp = run(
    f'curl -s -b /tmp/ss_cookies.txt http://127.0.0.1:8088/api/v1/security/csrf_token/ '
    f'-H "Authorization: Bearer {token}"'
)
csrf = json.loads(csrf_resp)["result"]
print(f"CSRF: {csrf[:20]}...")

# Helper to call API
def api(method, path, data=None):
    h = f'-H "Authorization: Bearer {token}" -H "Content-Type: application/json" -H "X-CSRFToken: {csrf}" -b /tmp/ss_cookies.txt'
    d = f'-d \'{json.dumps(data)}\'' if data else ''
    cmd = f'curl -s -X {method} http://127.0.0.1:8088/api/v1/{path} {h} {d}'
    return json.loads(run(cmd))

# Update chart params
charts_config = [
    (1, "Criticality Distribution", "bar_chart", {
        "metrics": [{"expressionType": "SIMPLE", "aggregate": "COUNT", "column": {"column_name": "company_id"}, "label": "COUNT(company_id)"}],
        "groupby": ["criticality"], "time_range": "No filter", "row_limit": 50
    }),
    (2, "Interpretation Breakdown", "pie", {
        "metrics": [{"expressionType": "SIMPLE", "aggregate": "COUNT", "column": {"column_name": "company_id"}, "label": "COUNT(company_id)"}],
        "groupby": ["interpretation"], "time_range": "No filter"
    }),
    (3, "Hypothesis Distribution", "bar_chart", {
        "metrics": [{"expressionType": "SIMPLE", "aggregate": "COUNT", "column": {"column_name": "company_id"}, "label": "COUNT(company_id)"}],
        "groupby": ["hypothesis_code"], "time_range": "No filter", "row_limit": 50
    }),
    (4, "Anomalies Table", "table", {
        "all_columns": ["company_id", "year", "hypothesis_code", "interpretation", "criticality", "criticality_score", "interpretation_reason"],
        "time_range": "No filter", "row_limit": 100
    }),
]

for cid, name, viz, params in charts_config:
    result = api("PUT", f"chart/{cid}", {
        "slice_name": name,
        "viz_type": viz,
        "datasource_id": 3,
        "datasource_type": "table",
        "params": json.dumps(params)
    })
    print(f"Chart {cid} ({name}): OK")

# Now setup dashboard layout with native filters
# Native filters are embedded in the dashboard's position_json
# We need to build a proper layout with filter boxes

# First, get the dashboard
dash = api("GET", "dashboard/2")
dash_data = dash.get("result", {})

# Update dashboard metadata with native filters configuration
# The position_json defines the dashboard layout including filter boxes
# and chart placements

dash_update = {
    "dashboard_title": "VectorNode: Anomalies & Economic Signals",
    "slug": "vectornode-anomalies",
    "description": "Analytical dashboard for anomaly detection and economic signal analysis based on test_dataset.csv",
    "published": True
}

result = api("PUT", "dashboard/2", dash_update)
print(f"Dashboard title updated: {result.get('result', {}).get('dashboard_title', 'error')}")

# Create proper position_json with native filters and chart layout
position_json = {
    "DASHBOARD_VERSION": "v2",
    "GRID_ID": {
        "children": [],
        "type": "GRID",
        "id": "GRID_ID",
        "meta": {}
    },
    "ROOT_ID": {
        "children": ["GRID_ID"],
        "type": "ROOT",
        "id": "ROOT_ID"
    }
}

# Add filter box as a native filter
native_filter = {
    "id": "NATIVE_FILTER-1",
    "type": "CHART",
    "id": "NATIVE_FILTER-1",
    "children": [],
    "meta": {
        "chartId": "native_filter",
        "width": 12,
        "height": 2,
        "sliceName": "Filters"
    }
}

# Add chart positions
for i, (cid, name, viz, params) in enumerate(charts_config):
    chart_key = f"CHART-{cid}"
    row = i // 2
    col = i % 2
    position_json[chart_key] = {
        "children": [],
        "type": "CHART",
        "id": chart_key,
        "meta": {
            "chartId": cid,
            "width": 6,
            "height": 8,
            "sliceName": name,
            "nativeFilterValues": []
        },
        "parents": ["ROOT_ID", "GRID_ID"]
    }
    # Add to grid
    position_json["GRID_ID"]["children"].append(chart_key)

# Set dashboard position
dash_pos = api("PUT", "dashboard/2", {
    "position_json": json.dumps(position_json)
})
print(f"Dashboard layout updated")

# Now set up filters using the dashboard's native_filter_configuration
# This is stored in the dashboard's json_metadata field
dash_detail = api("GET", "dashboard/2")
dash_result = dash_detail.get("result", {})

# Build native filters configuration
native_filters = [
    {
        "id": "NATIVE_FILTER-year",
        "filterType": "filter_select",
        "column": "year",
        "name": "Year",
        "defaultValue": None,
        "multiple": True,
        "dataset": 3,
        "inverseSelection": False,
        "adhoc_filters": [],
        "time_range": "No filter"
    },
    {
        "id": "NATIVE_FILTER-region",
        "filterType": "filter_select",
        "column": "region",
        "name": "Region",
        "defaultValue": None,
        "multiple": True,
        "dataset": 3,
        "inverseSelection": False
    },
    {
        "id": "NATIVE_FILTER-okved",
        "filterType": "filter_select",
        "column": "okved_section",
        "name": "Industry (OKVED)",
        "defaultValue": None,
        "multiple": True,
        "dataset": 3,
        "inverseSelection": False
    },
    {
        "id": "NATIVE_FILTER-interp",
        "filterType": "filter_select",
        "column": "interpretation",
        "name": "Interpretation",
        "defaultValue": None,
        "multiple": True,
        "dataset": 3,
        "inverseSelection": False
    },
    {
        "id": "NATIVE_FILTER-crit",
        "filterType": "filter_select",
        "column": "criticality",
        "name": "Criticality",
        "defaultValue": None,
        "multiple": True,
        "dataset": 3,
        "inverseSelection": False
    },
    {
        "id": "NATIVE_FILTER-hypo",
        "filterType": "filter_select",
        "column": "hypothesis_code",
        "name": "Hypothesis",
        "defaultValue": None,
        "multiple": True,
        "dataset": 3,
        "inverseSelection": False
    }
]

json_metadata = json.dumps({
    "native_filter_configuration": native_filters,
    "timed_refresh_immune_slices": [],
    "expanded_slices": {},
    "refresh_frequency": 0,
    "default_filters": "{}"
})

result = api("PUT", "dashboard/2", {
    "json_metadata": json_metadata
})
print(f"Native filters configured: {result.get('result', {}).get('dashboard_title', 'error')}")

ssh.close()
print("\nDashboard setup complete!")
