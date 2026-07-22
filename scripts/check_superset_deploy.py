import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

# Check how superset is started
stdin, stdout, stderr = ssh.exec_command(
    "docker inspect podft-superset --format '{{index .Config.Labels \"com.docker.compose.project\"}} {{index .Config.Labels \"com.docker.compose.service\"}}'"
)
print('Docker compose project:', stdout.read().decode(errors='replace').strip())

# Find all compose files in podft
stdin2, stdout2, stderr2 = ssh.exec_command(
    "find /opt/podft -name 'docker-compose*' -o -name 'compose*' 2>/dev/null"
)
print('\nCompose files:')
print(stdout2.read().decode(errors='replace').strip())

# Check command used to start superset
stdin3, stdout3, stderr3 = ssh.exec_command(
    "docker ps --filter name=superset --no-trunc --format '{{.Command}}'"
)
print('\nSuperset command:', stdout3.read().decode(errors='replace').strip()[:200])

ssh.close()
