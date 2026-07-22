import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', port=22, username='root', password='8884&JKL%f75', timeout=15)

# Export inside container
_, o, _ = ssh.exec_command(
    "docker exec podft-postgres psql -U podft -d analytics -c "
    "\"COPY analytics.v_company_dashboard TO '/tmp/v_comp_dash_export.csv' WITH CSV HEADER\""
)
print('Export:', o.read().decode(errors='replace')[:200])

# Copy from container to host
_, o2, _ = ssh.exec_command('docker cp podft-postgres:/tmp/v_comp_dash_export.csv /tmp/v_comp_dash_export.csv')
print('Cp to host:', o2.read().decode(errors='replace')[:100])

# Check size
_, o3, _ = ssh.exec_command('ls -lh /tmp/v_comp_dash_export.csv')
print('Size:', o3.read().decode(errors='replace').strip())

# Download
sftp = ssh.open_sftp()
sftp.get('/tmp/v_comp_dash_export.csv', r'D:\project\FRS_TEST\data\v_company_dashboard_export.csv')
sftp.close()
print('Downloaded to D:\\project\\FRS_TEST\\data\\v_company_dashboard_export.csv')

ssh.close()
