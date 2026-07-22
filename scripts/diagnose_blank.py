import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

# Get bootstrap data - full JSON
stdin, stdout, stderr = ssh.exec_command(
    "curl -s https://vectornode.ru/superset/login/ 2>&1 | grep -oP 'data-bootstrap=\"[^\"]*\"' | head -1"
)
bootstrap = stdout.read().decode(errors='replace').strip()
print('Full bootstrap (first 500):')
print(bootstrap[:500])

# Extract key URLs
stdin2, stdout2, stderr2 = ssh.exec_command(
    "curl -s https://vectornode.ru/superset/login/ 2>&1 | grep -oP 'user_login_url[^,}]*|user_logout_url[^,}]*|user_info_url[^,}]*|application_root[^,}]*'"
)
print('\nKey URLs:')
print(stdout2.read().decode(errors='replace').strip())

# Check Superset logs for recent errors
stdin3, stdout3, stderr3 = ssh.exec_command(
    'docker logs podft-superset --tail 50 2>&1'
)
print('\nSuperset recent logs:')
print(stdout3.read().decode(errors='replace').strip()[:2000])

ssh.close()
