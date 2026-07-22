import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

# Check if chart/data location was added
stdin, stdout, stderr = ssh.exec_command(
    "grep -A5 'chart/data' /etc/nginx/sites-enabled/vectornode.ru 2>/dev/null || echo 'NOT FOUND'"
)
print('Config check:')
print(stdout.read().decode(errors='replace').strip()[:500])

# If not found, add it manually inside the bi.vectornode.ru HTTPS block
stdin2, stdout2, stderr2 = ssh.exec_command(
    "grep -n 'bi.vectornode.ru' /etc/nginx/sites-enabled/vectornode.ru | head -3"
)
print('\nbi lines:')
print(stdout2.read().decode(errors='replace').strip()[:300])

# Read the full bi HTTPS block
stdin3, stdout3, stderr3 = ssh.exec_command(
    "grep -A30 'listen 443 ssl http2' /etc/nginx/sites-enabled/vectornode.ru | grep -B2 -A30 'bi.vectornode.ru' | head -40"
)
print('\nbi HTTPS block:')
print(stdout3.read().decode(errors='replace').strip()[:1000])

ssh.close()
