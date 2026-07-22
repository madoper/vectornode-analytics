import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=10)

# Read config and show the bi.vectornode.ru HTTPS server block
stdin, stdout, stderr = ssh.exec_command(
    "grep -n 'server_name bi\\|chart/data\\|location = \\|location /api\\|location / {' "
    "/etc/nginx/sites-enabled/vectornode.ru 2>/dev/null"
)
print(stdout.read().decode(errors='replace').strip())

ssh.close()
