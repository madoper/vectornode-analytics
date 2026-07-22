import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=10)

# Check nginx access log for recent chart/data requests
_, o, _ = ssh.exec_command(
    "tail -50 /var/log/nginx/access.log | grep 'chart/data'"
)
print('Access log (chart/data):')
print(o.read().decode(errors='replace') or 'No entries')

# Check nginx error log
_, o2, _ = ssh.exec_command(
    "tail -20 /var/log/nginx/error.log"
)
print('\nError log:')
print(o2.read().decode(errors='replace') or 'No entries')

# Check full bi server block on server
_, o3, _ = ssh.exec_command(
    "sed -n '/server_name bi.vectornode.ru;/,/^}/p' /etc/nginx/sites-available/podft"
)
print('\nFull bi block:')
print(o3.read().decode(errors='replace'))

ssh.close()
