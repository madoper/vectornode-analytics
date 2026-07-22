import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

# Find the log file
cmd = 'find /opt/analytics/logs -path "*manual_005*" -name "*.log" 2>/dev/null'
stdin, stdout, stderr = ssh.exec_command(cmd)
print('Log files:')
print(stdout.read().decode(errors='replace').strip())

# Check the staging schema
cmd2 = "docker exec podft-postgres psql -U podft -d analytics -c \"\dn\" 2>&1"
stdin2, stdout2, stderr2 = ssh.exec_command(cmd2)
print('\nSchemas:', stdout2.read().decode(errors='replace').strip())

ssh.close()
