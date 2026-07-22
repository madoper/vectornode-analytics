import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

stdin, stdout, stderr = ssh.exec_command('wc -l /opt/analytics/data/test_dataset.csv')
print('Lines:', stdout.read().decode(errors='replace').strip())

stdin2, stdout2, stderr2 = ssh.exec_command("docker exec podft-postgres psql -U podft -d analytics -c \"SELECT COUNT(DISTINCT company_id) FROM staging.test_dataset\" 2>&1")
print('Companies in staging:', stdout2.read().decode(errors='replace').strip())

ssh.close()
