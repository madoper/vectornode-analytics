import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=10)

# Check mounts
_, o, _ = ssh.exec_command(
    'docker inspect podft-superset --format "{{range .Mounts}}{{.Source}} -> {{.Destination}} {{println}}{{end}}"'
)
print('Mounts:')
print(o.read().decode(errors='replace'))

# Check if config is a mount or baked in
_, o2, _ = ssh.exec_command(
    'ls -la /opt/podft/infra/superset-init/superset_config.py 2>/dev/null && echo "EXISTS" || echo "NOT_FOUND"'
)
print('\nHost config:', o2.read().decode(errors='replace'))

ssh.close()
