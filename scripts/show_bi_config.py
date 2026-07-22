import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=10)

# Show the full podft config (active)
_, o, _ = ssh.exec_command("grep -n '' /etc/nginx/sites-available/podft")
lines = o.read().decode(errors='replace').split('\n')
in_bi = False
for line in lines:
    if 'server_name bi.vectornode.ru' in line and 'return 301' not in line:
        in_bi = True
    if in_bi:
        print(line)
        if line.strip() == '}' and not 'else' in line and not 'then' in line:
            # Check if this is the closing of the server block
            break

ssh.close()
