import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

# Check docker inspect for volumes and read-only status
stdin, stdout, stderr = ssh.exec_command(
    "docker inspect podft-superset --format '{{.HostConfig.ReadonlyRootfs}} {{range .Mounts}}{{.Destination}} {{end}}'"
)
print('Read-only + Mounts:', stdout.read().decode(errors='replace').strip())

# Check if there's /tmp writable
stdin2, stdout2, stderr2 = ssh.exec_command(
    'docker exec podft-superset touch /tmp/test_write && echo writable || echo not_writable'
)
print('/tmp:', stdout2.read().decode(errors='replace').strip())

ssh.close()
