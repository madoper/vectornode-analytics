import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

# Check config for APPLICATION_ROOT
stdin, stdout, stderr = ssh.exec_command('grep -i "application_root\\|script_root\\|prefix" /opt/podft/infra/superset-init/superset_config.py')
print('Config:', stdout.read().decode(errors='replace').strip())

# Check the curl response directly - does brand.path get double from somewhere?
stdin2, stdout2, stderr2 = ssh.exec_command(
    "curl -s https://vectornode.ru/superset/login/ 2>&1 | grep -oP 'brand.*?path[^,}]*'"
)
print('Brand path in HTML:', stdout2.read().decode(errors='replace').strip())

# Check if it's different without any prefix
stdin3, stdout3, stderr3 = ssh.exec_command(
    "curl -s http://127.0.0.1:8088/login/ 2>&1 | grep -oP 'brand.*?path[^,}]*'"
)
print('Brand path direct (no nginx):', stdout3.read().decode(errors='replace').strip())

ssh.close()
