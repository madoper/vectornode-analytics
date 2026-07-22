import paramiko, json, time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

def run(cmd):
    stdin, stdout, stderr = ssh.exec_command(cmd)
    return stdout.read().decode(errors='replace').strip()

# First, get a session cookie via the web login endpoint
login_cmd = (
    'rm -f /tmp/ss_final.txt && '
    'curl -s -c /tmp/ss_final.txt -L -X POST http://127.0.0.1:8088/login/ '
    '-d "username=admin&password=admin" '
    '-H "Content-Type: application/x-www-form-urlencoded" '
    '-H "Referer: http://127.0.0.1:8088/login/" 2>&1'
)
login_result = run(login_cmd)

# Check if we got a session by trying to access the welcome page
check_cmd = 'curl -s -b /tmp/ss_final.txt -o /dev/null -w "%{http_code}" http://127.0.0.1:8088/superset/welcome/ 2>&1'
check = run(check_cmd)
print(f"Session check (welcome page): {check}")

# Get CSRF token with session cookie
csrf_cmd = 'curl -s -b /tmp/ss_final.txt http://127.0.0.1:8088/api/v1/security/csrf_token/ 2>&1'
csrf_resp = run(csrf_cmd)
print(f"CSRF: {csrf_resp[:100]}")

csrf = json.loads(csrf_resp).get("result", "")
print(f"CSRF token: {csrf[:20]}...")

# Now try to update dashboard
if csrf:
    update_cmd = (
        f'curl -s -X PUT http://127.0.0.1:8088/api/v1/dashboard/2 '
        f'-H "Content-Type: application/json" '
        f'-H "X-CSRFToken: {csrf}" '
        f'-b /tmp/ss_final.txt '
        f'-d \'{{"dashboard_title":"VectorNode: Anomalies & Economic Signals","slug":"vectornode-anomalies","published":true}}\' 2>&1'
    )
    result = run(update_cmd)
    print(f"\nDashboard update result: {result[:300]}")

    # Update dashboard with native filters JSON metadata
    native_filters_json = json.dumps({
        "native_filter_configuration": [
            {"id":"NF-year","filterType":"filter_select","column":"year","name":"Year","multiple":True,"dataset":3},
            {"id":"NF-region","filterType":"filter_select","column":"region","name":"Region","multiple":True,"dataset":3},
            {"id":"NF-okved","filterType":"filter_select","column":"okved_section","name":"Industry","multiple":True,"dataset":3},
            {"id":"NF-interp","filterType":"filter_select","column":"interpretation","name":"Interpretation","multiple":True,"dataset":3},
            {"id":"NF-crit","filterType":"filter_select","column":"criticality","name":"Criticality","multiple":True,"dataset":3},
            {"id":"NF-hypo","filterType":"filter_select","column":"hypothesis_code","name":"Hypothesis","multiple":True,"dataset":3}
        ]
    })
    
    meta_cmd = (
        f'curl -s -X PUT http://127.0.0.1:8088/api/v1/dashboard/2 '
        f'-H "Content-Type: application/json" '
        f'-H "X-CSRFToken: {csrf}" '
        f'-b /tmp/ss_final.txt '
        f'-d \'{{"json_metadata":{json.dumps(native_filters_json)}}}\' 2>&1'
    )
    result2 = run(meta_cmd)
    print(f"\nJSON metadata update: {result2[:300]}")

ssh.close()
