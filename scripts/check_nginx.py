import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=10)

# Check sites-enabled
_, o, _ = ssh.exec_command('ls -la /etc/nginx/sites-enabled/')
print('sites-enabled:')
print(o.read().decode(errors='replace'))

# Check if bi.vectornode.ru block has chart/data redirect
_, o2, _ = ssh.exec_command('grep -c "chart/data" /etc/nginx/sites-enabled/vectornode.ru')
count = o2.read().decode(errors='replace').strip()
print(f'\nchart/data references in enabled config: {count}')

# Show the bi server block
_, o3, _ = ssh.exec_command("sed -n '/server_name bi.vectornode.ru/,/^}/p' /etc/nginx/sites-enabled/vectornode.ru | head -40")
print('\nbi server block (first 40 lines):')
print(o3.read().decode(errors='replace'))

ssh.close()
