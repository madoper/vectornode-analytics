import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15, look_for_keys=False, allow_agent=False)

# Verify all endpoints work via nginx proxy
cmds = [
    "curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:8501/ 2>/dev/null",
    "curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:8501/_stcore/health 2>/dev/null",
    "curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:8501/_stcore/stream 2>/dev/null",
]

for cmd in cmds:
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=8)
    print(stdout.read().decode().strip()[:200])

ssh.close()
