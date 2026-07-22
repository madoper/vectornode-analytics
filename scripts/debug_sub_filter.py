import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

stdin, stdout, stderr = ssh.exec_command(
    "grep -n 'sub_filter' /etc/nginx/sites-enabled/vectornode.ru | tail -3"
)
lines = stdout.read().decode('utf-8', errors='replace')
print(repr(lines))

# Also check what response has
stdin2, stdout2, stderr2 = ssh.exec_command(
    "curl -s https://vectornode.ru/superset/login/ 2>&1 | head -3"
)
print('\nHTML head:')
print(stdout2.read().decode(errors='replace').strip()[:300])

ssh.close()
