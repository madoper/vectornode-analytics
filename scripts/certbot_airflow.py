import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

cmd = (
    'certbot --nginx -d airflow.vectornode.ru --non-interactive --agree-tos '
    '--email admin@vectornode.ru --expand 2>&1'
)

print(f'> {cmd[:60]}...')
stdin, stdout, stderr = ssh.exec_command(cmd)
print(stdout.read().decode(errors='replace'))
ssh.close()
