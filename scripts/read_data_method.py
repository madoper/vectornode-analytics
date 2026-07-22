import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=10)

# Read lines 180-350 of chart data API (the data method)
stdin, stdout, stderr = ssh.exec_command(
    "docker exec podft-superset sed -n '180,380p' /app/superset/charts/data/api.py 2>/dev/null"
)
print(stdout.read().decode(errors='replace').strip()[:3000])

ssh.close()
