import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

stdin, stdout, stderr = ssh.exec_command(
    "grep -n 'sub_filter.*head\\|_fixSS\\|_p.apply\\|JSON.parse' /etc/nginx/sites-enabled/vectornode.ru"
)
print('Sub_filter lines:')
print(stdout.read().decode(errors='replace').strip())

# Check if the old pattern is still there
stdin2, stdout2, stderr2 = ssh.exec_command(
    "grep '_fixSS' /etc/nginx/sites-enabled/vectornode.ru"
)
print(f'\n_fixSS found: {stdout2.read().decode(errors="replace").strip()}')

# Check if the new pattern was added somehow
stdin3, stdout3, stderr3 = ssh.exec_command(
    "grep '_p.apply' /etc/nginx/sites-enabled/vectornode.ru"
)
print(f'_p.apply found: {stdout3.read().decode(errors="replace").strip()}')

# Show the actual sub_filter lines
stdin4, stdout4, stderr4 = ssh.exec_command(
    "grep 'sub_filter' /etc/nginx/sites-enabled/vectornode.ru"
)
print('\nAll sub_filter:')
print(stdout4.read().decode(errors='replace').strip())

ssh.close()
