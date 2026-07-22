import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=10)

# Check if redirect block exists
stdin, stdout, stderr = ssh.exec_command(
    "grep -A5 'chart/data' /etc/nginx/sites-enabled/vectornode.ru 2>/dev/null"
)
print('Config:')
print(stdout.read().decode(errors='replace').strip()[:500])

# Test redirect via localhost HTTP
stdin2, stdout2, stderr2 = ssh.exec_command(
    'curl -s -i -X POST "http://127.0.0.1/api/v1/chart/data?form_data={\\"slice_id\\":1}" '
    '-H "Host: bi.vectornode.ru" 2>&1 | head -15'
)
print('\nHTTP redirect test:')
lines = stdin2[1].read().decode(errors='replace').strip().split('\n')
for line in lines[:12]:
    print(line[:200])

ssh.close()
