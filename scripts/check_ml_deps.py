import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

cmd = '. /opt/analytics/venv/bin/activate && pip list 2>/dev/null | grep -iE "scikit|pandas|sqlalchemy|psycopg"'
stdin, stdout, stderr = ssh.exec_command(cmd)
print(stdout.read().decode(errors='replace').strip())
ssh.close()
