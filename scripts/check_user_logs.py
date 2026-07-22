import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=10)

# Check latest requests from the user
_, o, _ = ssh.exec_command(
    'tail -30 /var/log/nginx/access.log | grep "37.110"'
)
print('User requests:')
print(o.read().decode(errors='replace') or 'No requests from user IP')

# Check all recent chart/data requests
_, o2, _ = ssh.exec_command(
    'tail -50 /var/log/nginx/access.log | grep "chart/data"'
)
print('\nAll chart/data:')
print(o2.read().decode(errors='replace') or 'None')

ssh.close()
