import paramiko, json

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

# Login
cmd = ('curl -s -X POST http://127.0.0.1:8088/api/v1/security/login '
       '-H "Content-Type: application/json" '
       '-d \'{"username":"admin","password":"admin","provider":"db"}\'')
stdin, stdout, stderr = ssh.exec_command(cmd)
resp = json.loads(stdout.read().decode())
token = resp['access_token']

# Add analytics database
db_payload = json.dumps({
    "database_name": "Analytics (dbt)",
    "sqlalchemy_uri": "postgresql://dbt_user:dbt_pass@podft-postgres:5432/analytics",
    "expose_in_sql_lab": True,
    "allow_run_async": True,
    "allow_dml": False
})

cmd2 = f'curl -s -X POST http://127.0.0.1:8088/api/v1/database/ ' \
       f'-H "Authorization: Bearer {token}" ' \
       f'-H "Content-Type: application/json" ' \
       f'-d \'{db_payload}\''

stdin2, stdout2, stderr2 = ssh.exec_command(cmd2)
result = json.loads(stdout2.read().decode())
print('DB creation:', json.dumps(result, indent=2, ensure_ascii=False)[:500])

ssh.close()
