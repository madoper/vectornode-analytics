import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

sftp = ssh.open_sftp()
sftp.put(r'D:\project\FRS_TEST\scripts\ddl.sql', '/tmp/ddl.sql')
sftp.close()

stdin, stdout, stderr = ssh.exec_command(
    'docker exec -i podft-postgres psql -U podft -d analytics < /tmp/ddl.sql 2>&1'
)
print(stdout.read().decode(errors='replace').strip())

ssh.close()
