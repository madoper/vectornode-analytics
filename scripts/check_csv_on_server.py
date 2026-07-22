import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

stdin, stdout, stderr = ssh.exec_command('wc -l /opt/analytics/data/test_dataset.csv')
print('Lines:', stdout.read().decode(errors='replace').strip())

stdin2, stdout2, stderr2 = ssh.exec_command('head -1 /opt/analytics/data/test_dataset.csv && tail -1 /opt/analytics/data/test_dataset.csv')
print('First/last lines:')
print(stdout2.read().decode(errors='replace').strip())

ssh.close()
