import paramiko, os
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', port=22, username='root', password='8884&JKL%f75', timeout=15)

tables = ["rpt_anomaly", "rpt_company_hypothesis_flags", "rpt_company_year", "rpt_group_signal", "rpt_hypothesis_summary"]

for tbl in tables:
    print(f'Exporting {tbl}...')
    
    # Use COPY TO file inside container (postgres user can write to /tmp inside container)
    cmd = f'docker exec podft-postgres psql -U podft -d analytics -c "COPY reporting.{tbl} TO STDOUT WITH CSV HEADER" > /tmp/{tbl}.csv'
    stdin,stdout,stderr = ssh.exec_command(cmd)
    err = stderr.read().decode(errors='replace')
    out = stdout.read().decode(errors='replace')
    if err:
        print(f'  ERR: {err[:100]}')
    
    # Check file
    stdin2,stdout2,stderr2 = ssh.exec_command(f'ls -la /tmp/{tbl}.csv 2>&1')
    check = stdout2.read().decode(errors='replace').strip()
    if 'No such' in check:
        print(f'  FAIL: file not created')
        continue
    
    # Download via sftp
    local_path = rf'D:\project\FRS_TEST\data\{tbl}.csv'
    try:
        sftp = ssh.open_sftp()
        sftp.get(f'/tmp/{tbl}.csv', local_path)
        sftp.close()
        size = os.path.getsize(local_path)
        print(f'  OK: {size:,} bytes -> {local_path}')
    except Exception as e:
        # Fallback: read via ssh and write locally
        print(f'  SFTP failed ({e}), trying ssh cat...')
        stdin3,stdout3,stderr3 = ssh.exec_command(f'cat /tmp/{tbl}.csv')
        data = stdout3.read().decode(errors='replace')
        with open(local_path, 'w', encoding='utf-8') as f:
            f.write(data)
        size = os.path.getsize(local_path)
        print(f'  OK (ssh): {size:,} bytes -> {local_path}')

ssh.close()
print('\nDone!')
