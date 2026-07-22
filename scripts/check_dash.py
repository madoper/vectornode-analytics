import paramiko, json

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

def run(cmd):
    stdin, stdout, stderr = ssh.exec_command(cmd)
    return stdout.read().decode(errors='replace').strip()

# Login
login = run(
    'curl -s -c /tmp/ss_c.txt -X POST http://127.0.0.1:8088/api/v1/security/login '
    '-H "Content-Type: application/json" '
    '-d \'{"username":"admin","password":"admin","provider":"db"}\''
)
token = json.loads(login)["access_token"]

csrf_resp = run(
    f'curl -s -b /tmp/ss_c.txt http://127.0.0.1:8088/api/v1/security/csrf_token/ '
    f'-H "Authorization: Bearer {token}"'
)
csrf = json.loads(csrf_resp)["result"]

def api(method, path, data=None):
    h = f'-H "Authorization: Bearer {token}" -H "Content-Type: application/json" -H "X-CSRFToken: {csrf}" -b /tmp/ss_c.txt'
    d = f'-d \'{json.dumps(data)}\'' if data else ''
    cmd = f'curl -s -X {method} http://127.0.0.1:8088/api/v1/{path} {h} {d}'
    return run(cmd)

# Try to update dashboard title
result = api("PUT", "dashboard/2", {
    "dashboard_title": "VectorNode: Anomalies & Economic Signals",
    "slug": "vectornode-anomalies",
    "description": "Analytical dashboard for anomaly detection and economic signal analysis",
    "published": True
})
print("Dashboard update:")
print(result[:500])

# Try to get the current dashboard to see its structure
dash = api("GET", "dashboard/2")
print("\nDashboard detail:")
print(dash[:500])

ssh.close()
