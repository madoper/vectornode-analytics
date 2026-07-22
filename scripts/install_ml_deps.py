import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

cmds = [
    '. /opt/analytics/venv/bin/activate && pip install scikit-learn pandas sqlalchemy psycopg2-binary -q 2>&1 | tail -3',
]

for cmd in cmds:
    print(f'> {cmd[:80]}')
    stdin, stdout, stderr = ssh.exec_command(cmd)
    for line in iter(stdout.readline, ''):
        print(line.strip())
    ssh.close()
