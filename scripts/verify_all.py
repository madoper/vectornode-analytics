import paramiko, json
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', port=22, username='root', password='8884&JKL%f75', timeout=10)

# Check ALL charts for duplicate labels in columns
for cid in range(1, 7):
    _, o, _ = ssh.exec_command(
        "docker exec podft-postgres psql -U podft -d superset -t -A -c "
        "\"SELECT LEFT(query_context, 500) FROM slices WHERE id = " + str(cid) + "\""
    )
    qc_preview = o.read().decode(errors='replace').strip()
    # Count columns array
    if '"columns":' in qc_preview:
        cols_part = qc_preview.split('"columns":')[1].split('],')[0] + ']'
        count_crit = cols_part.count('criticality') + cols_part.count('"criticality"')
        count_hyp = cols_part.count('hypothesis_code')
        if count_crit > 1 or count_hyp > 1:
            print(f'Chart {cid}: potential duplicate (criticality={count_crit}, hypothesis_code={count_hyp})')

# Test all charts
_, auth, _ = ssh.exec_command(
    'curl -s -X POST http://127.0.0.1:8088/api/v1/security/login '
    '-H "Content-Type: application/json" '
    '-d \'{"username":"admin","password":"admin","provider":"db"}\''
)
token = json.loads(auth.read().decode(errors='replace'))["access_token"]

import urllib.parse
print('\nAll charts test:')
for cid in range(1, 7):
    fd = urllib.parse.quote(f'{{"slice_id":{cid}}}')
    _, co, _ = ssh.exec_command(
        'curl -s -w "%{http_code}" -X POST "http://127.0.0.1:8088/api/v1/chart/data?form_data=' + fd + '" '
        '-H "Content-Type: application/json" '
        '-H "Authorization: Bearer ' + token + '" '
        '-o /dev/null'
    )
    code = co.read().decode(errors='replace').strip()
    status = 'OK' if code in ('200', '302') else f'FAIL({code})'
    print(f'  Chart {cid}: {status}')

ssh.close()
