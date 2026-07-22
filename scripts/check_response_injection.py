import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

# Check exact response head
stdin, stdout, stderr = ssh.exec_command(
    "curl -s https://vectornode.ru/superset/login/ 2>&1 | head -6"
)
print(repr(stdout.read().decode(errors='replace')))

# Check if indexOf is present
stdin2, stdout2, stderr2 = ssh.exec_command(
    "curl -s https://vectornode.ru/superset/login/ 2>&1 | grep -c 'indexOf'"
)
print(f'\nindexOf in response: {stdout2.read().decode(errors="replace").strip()}')

# Check if JSON.parse is present
stdin3, stdout3, stderr3 = ssh.exec_command(
    "curl -s https://vectornode.ru/superset/login/ 2>&1 | grep -c 'JSON.parse'"
)
print(f'JSON.parse in response: {stdout3.read().decode(errors="replace").strip()}')

ssh.close()
