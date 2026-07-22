import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=10)

# Show full bi server block from podft
_, o, _ = ssh.exec_command("grep -n '' /etc/nginx/sites-available/podft")
lines = o.read().decode(errors='replace').split('\n')
in_bi = False
count = 0
for line in lines:
    if 'server_name bi.vectornode.ru' in line:
        in_bi = True
        count = 0
    if in_bi:
        print(line)
        count += 1
        if count > 2 and line.strip() == '}':
            break

ssh.close()
