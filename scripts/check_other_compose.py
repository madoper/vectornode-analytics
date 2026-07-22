import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

cmds = [
    "cat /opt/podft/docker-compose.vps.yml",
    "cat /opt/podft/docker-compose.monolith.yml",
]

for cmd in cmds:
    print(f'=== {cmd.split("/")[-1]} ===')
    stdin, stdout, stderr = ssh.exec_command(cmd)
    print(stdout.read().decode(errors='replace').strip()[:2000])

ssh.close()
