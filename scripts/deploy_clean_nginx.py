import paramiko, json
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=10)

sftp = ssh.open_sftp()
sftp.put(r'D:\project\FRS_TEST\nginx\vectornode.conf', '/etc/nginx/sites-available/podft')
sftp.close()

# Test & reload
_, o, _ = ssh.exec_command('nginx -t 2>&1')
print('nginx -t:', o.read().decode(errors='replace').strip())

# Check no chart/data redirect
_, o_check, _ = ssh.exec_command('grep "chart/data" /etc/nginx/sites-available/podft')
print('chart/data refs:', o_check.read().decode(errors='replace') or 'NONE')

_, o2, _ = ssh.exec_command('nginx -s reload 2>&1')
print('reload:', o2.read().decode(errors='replace').strip())

# Test: chart POST with form_data in query AND body
_, auth, _ = ssh.exec_command(
    'curl -s -X POST http://127.0.0.1:8088/api/v1/security/login -H "Content-Type: application/json" -d \'{"username":"admin","password":"admin","provider":"db"}\''
)
token = json.loads(auth.read().decode())["access_token"]

# Chart type POST (with JSON body)
import urllib.parse
fd = urllib.parse.quote('{"slice_id":5}')
_, o3, _ = ssh.exec_command(
    'curl -s -k -w "\nHTTP_%{http_code}" -X POST "https://bi.vectornode.ru/api/v1/chart/data?form_data=' + fd + '&dashboard_id=2" '
    '-H "Content-Type: application/json" '
    '-H "Authorization: Bearer ' + token + '" '
    '-d \'{"datasource":{"id":3,"type":"table"},"queries":[{"groupby":["criticality"],"metrics":[{"aggregate":"COUNT","column":{"column_name":"company_id"},"expressionType":"SIMPLE"}]}],"form_data":{"viz_type":"table","datasource":"3__table"}}\''
)
print('\nChart POST (with body):')
print(o3.read().decode(errors='replace')[:500])

# Native filter POST
_, o4, _ = ssh.exec_command(
    'curl -s -k -w "\nHTTP_%{http_code}" -X POST https://bi.vectornode.ru/api/v1/chart/data '
    '-H "Content-Type: application/json" '
    '-H "Authorization: Bearer ' + token + '" '
    '-d \'{"datasource":{"id":3,"type":"table"},"queries":[{"columns":["year"],"row_limit":5}]}\''
)
print('\n\nNative filter POST:')
print(o4.read().decode(errors='replace')[:400])

ssh.close()
