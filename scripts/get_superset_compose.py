import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

# Get full superset service definition from compose file
stdin, stdout, stderr = ssh.exec_command(
    "cat /opt/podft/docker-compose.yml | grep -A 30 'superset:'"
)
print('Superset service:')
print(stdout.read().decode(errors='replace').strip())

ssh.close()
