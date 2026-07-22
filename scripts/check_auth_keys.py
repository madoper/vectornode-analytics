import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

stdin, stdout, stderr = ssh.exec_command('wc -l /root/.ssh/authorized_keys && tail -3 /root/.ssh/authorized_keys')
print(stdout.read().decode(errors='replace').strip()[:500])

# Test SSH with key-based auth
stdin2, stdout2, stderr2 = ssh.exec_command('sshd -T 2>&1 | grep -i "pubkey\|authorized" | head -3')
print('\nSSHD config:', stdout2.read().decode(errors='replace').strip()[:500])

ssh.close()
