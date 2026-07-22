import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', port=22, username='root', password='8884&JKL%f75', timeout=15)

# Copy from container to host, then download
_, o, _ = ssh.exec_command('docker cp podft-postgres:/tmp/v_comp_dash_v2.csv /tmp/v_comp_dash_v2.csv')
print('cp:', o.read().decode(errors='replace')[:100])

_, o2, _ = ssh.exec_command('ls -lh /tmp/v_comp_dash_v2.csv')
sftp = ssh.open_sftp()
sftp.get('/tmp/v_comp_dash_v2.csv', r'D:\project\FRS_TEST\data\v_company_dashboard_v2.csv')
sftp.close()
print('Downloaded:', o2.read().decode(errors='replace').strip())

ssh.close()
