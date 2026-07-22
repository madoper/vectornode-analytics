import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', port=22, username='root', password='8884&JKL%f75', timeout=15)

# Export CSV on server
_, o, _ = ssh.exec_command(
    'docker exec podft-postgres psql -U podft -d analytics '
    '-c "COPY analytics.v_company_dashboard TO STDOUT WITH CSV HEADER" '
    '> /tmp/v_company_dashboard.csv'
)
print('Export:', o.read().decode(errors='replace')[:200])

# Check file size
_, o2, _ = ssh.exec_command('ls -lh /tmp/v_company_dashboard.csv')
print('File:', o2.read().decode(errors='replace'))

# Download via SFTP
sftp = ssh.open_sftp()
sftp.get('/tmp/v_company_dashboard.csv', r'D:\project\FRS_TEST\data\v_company_dashboard.csv')
sftp.close()
print('Downloaded to D:\\project\\FRS_TEST\\data\\v_company_dashboard.csv')

ssh.close()
