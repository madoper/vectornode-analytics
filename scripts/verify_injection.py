import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

# Check HTML head section
stdin, stdout, stderr = ssh.exec_command(
    "curl -s https://vectornode.ru/superset/login/ 2>&1 | head -10"
)
print('HTML start:')
print(stdout.read().decode(errors='replace').strip()[:500])

# Check if JS injection is present
stdin2, stdout2, stderr2 = ssh.exec_command(
    "curl -s https://vectornode.ru/superset/login/ 2>&1 | grep -c 'fixBootstrap\\|DOMContentLoaded\\|application_root.*superset'"
)
print(f'\nInjection matches: {stdout2.read().decode(errors="replace").strip()}')

# Check hello endpoint  
stdin3, stdout3, stderr3 = ssh.exec_command(
    "curl -s https://vectornode.ru/superset/health 2>&1"
)
print(f'Health: {stdout3.read().decode(errors="replace").strip()}')

ssh.close()
