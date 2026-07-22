import paramiko, os
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', port=22, username='root', password='8884&JKL%f75', timeout=15)

tables = [
    ("analytics", "company"),
    ("analytics", "company_year"),
    ("analytics", "company_features"),
    ("analytics", "company_growth"),
    ("analytics", "company_zscore"),
    ("analytics", "anomaly"),
    ("analytics", "group_signal"),
    ("analytics", "v_company_dashboard"),
    ("staging", "test_dataset"),
]

for schema, tbl in tables:
    fname = f'{schema}_{tbl}'
    print(f'{fname}...', end=' ')
    
    cmd = f'docker exec podft-postgres psql -U podft -d analytics -c "COPY {schema}.{tbl} TO STDOUT WITH CSV HEADER" > /tmp/{fname}.csv'
    stdin,stdout,stderr = ssh.exec_command(cmd)
    stderr.read()
    stdout.read()
    
    stdin2,stdout2,stderr2 = ssh.exec_command(f'ls -la /tmp/{fname}.csv 2>&1')
    check = stdout2.read().decode(errors='replace').strip()
    if 'No such' in check:
        print('FAIL')
        continue
    
    local = rf'D:\project\FRS_TEST\data\{fname}.csv'
    try:
        sftp = ssh.open_sftp()
        sftp.get(f'/tmp/{fname}.csv', local)
        sftp.close()
        sz = os.path.getsize(local)
        print(f'{sz:,} bytes')
    except:
        stdin3,stdout3,stderr3 = ssh.exec_command(f'cat /tmp/{fname}.csv')
        data = stdout3.read().decode(errors='replace')
        with open(local, 'w', encoding='utf-8') as f:
            f.write(data)
        sz = os.path.getsize(local)
        print(f'{sz:,} bytes (ssh)')

ssh.close()
print('\nAll done!')
