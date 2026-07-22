import paramiko, os
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', port=22, username='root', password='8884&JKL%f75', timeout=15)

tables = [
    "rpt_anomaly",
    "rpt_company_hypothesis_flags",
    "rpt_company_year",
    "rpt_group_signal",
    "rpt_hypothesis_summary",
]

for tbl in tables:
    print(f'Exporting {tbl}...')
    
    # Step 1: COPY to file inside container
    _, o1, _ = ssh.exec_command(
        'docker exec podft-postgres psql -U podft -d analytics '
        f'-c "COPY reporting.{tbl} TO STDOUT WITH CSV HEADER" '
        f'> /tmp/{tbl}_raw.csv 2>&1'
    )
    o1.read()  # consume
    
    # Step 2: Copy from container to host using sh
    _, o2, _ = ssh.exec_command(
        f'docker cp podft-postgres:/tmp/{tbl}_raw.csv /tmp/{tbl}.csv'
    )
    o2.read()

    # Step 3: Check
    _, o3, _ = ssh.exec_command(f"ls -la /tmp/{tbl}.csv 2>&1 || echo 'NOT_FOUND'")
    result = o3.read().decode(errors='replace').strip()
    print(f'  Host: {result[:80]}')
    
    if 'NOT_FOUND' not in result:
        # Step 4: Download
        try:
            sftp = ssh.open_sftp()
            sftp.get(f'/tmp/{tbl}.csv', rf'D:\project\FRS_TEST\data\{tbl}.csv')
            sftp.close()
            local_size = os.path.getsize(rf'D:\project\FRS_TEST\data\{tbl}.csv')
            print(f'  Downloaded: {local_size:,} bytes')
        except Exception as e:
            print(f'  Download error: {e}')
            
            # Fallback: try with ssh cat
            try:
                _, o4, _ = ssh.exec_command(f'cat /tmp/{tbl}.csv')
                data = o4.read().decode(errors='replace')
                path = rf'D:\project\FRS_TEST\data\{tbl}.csv'
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(data)
                local_size = os.path.getsize(path)
                print(f'  Downloaded via cat: {local_size:,} bytes')
            except Exception as e2:
                print(f'  Cat fallback error: {e2}')
    else:
        print(f'  File not found on host')

print('\nDone!')
ssh.close()
