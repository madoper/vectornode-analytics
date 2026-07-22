import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

# Remove SUPERSET_BASE_URL from compose file
stdin, stdout, stderr = ssh.exec_command('cat /opt/podft/docker-compose.vps.yml')
compose = stdout.read().decode('utf-8', errors='replace')

compose = compose.replace('      SUPERSET_BASE_URL: /superset\n', '')
print('Removed SUPERSET_BASE_URL')

# Write back
import base64
cfg_b64 = base64.b64encode(compose.encode()).decode()
ssh.exec_command(f'echo {cfg_b64} | base64 -d > /opt/podft/docker-compose.vps.yml')

# Verify
stdin2, stdout2, stderr2 = ssh.exec_command('grep SUPERSET_BASE_URL /opt/podft/docker-compose.vps.yml || echo "NOT FOUND"')
print('Check:', stdout2.read().decode(errors='replace').strip())

# Recreate superset container with new env
stdin3, stdout3, stderr3 = ssh.exec_command(
    'cd /opt/podft && docker compose -f docker-compose.yml -f docker-compose.vps.yml up -d superset --force-recreate --no-deps 2>&1'
)
import time
for _ in range(20):
    line = stdout3.readline()
    if line:
        print(line.strip())
    else:
        break
time.sleep(5)

# Check status
stdin4, stdout4, stderr4 = ssh.exec_command('docker ps --filter name=superset --format "{{.Names}} {{.Status}}"')
print('Status:', stdout4.read().decode(errors='replace').strip())

ssh.close()
