import paramiko
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
    # Export inside container
    _, o, _ = ssh.exec_command(
        'docker exec podft-postgres psql -U podft -d analytics -c '
        f'"COPY reporting.{tbl} TO \'/tmp/{tbl}.csv\' WITH CSV HEADER"'
    )
    # Copy to host
    _, o2, _ = ssh.exec_command(f'docker cp podft-postgres:/tmp/{tbl}.csv /tmp/{tbl}.csv')
    # Check size
    _, o3, _ = ssh.exec_command(f'ls -lh /tmp/{tbl}.csv')
    size = o3.read().decode(errors='replace').strip()
    # Download
    sftp = ssh.open_sftp()
    sftp.get(f'/tmp/{tbl}.csv', f'D:\\project\\FRS_TEST\\data\\{tbl}.csv')
    sftp.close()
    print(f'  {tbl}.csv: {size}')

print('\nDone. Files:')
import os
for tbl in tables:
    path = f'D:\\project\\FRS_TEST\\data\\{tbl}.csv'
    print(f'  {path} ({os.path.getsize(path):,} bytes)')

ssh.close()
