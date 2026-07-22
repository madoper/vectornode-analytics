import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

# Fix Nginx config - remove the broken variable rules, use direct approach
sftp = ssh.open_sftp()
with sftp.open('/etc/nginx/sites-enabled/vectornode.ru', 'r') as f:
    cfg = f.read().decode('utf-8', errors='replace')

# Check what we have
print('Current sub_filter section:')
import re
# Find the sub_filter lines in the /superset/ location
for line in cfg.split('\n'):
    if 'sub_filter' in line:
        print(line)

ssh.close()
