import paramiko
import os

host = "62.217.183.95"
user = "root"
password = "8884&JKL%f75"

with open(os.path.expanduser("~/.ssh/frstest_key.pub")) as f:
    pubkey = f.read().strip()

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(host, username=user, password=password)

stdin, stdout, stderr = client.exec_command("mkdir -p ~/.ssh && chmod 700 ~/.ssh")
stdout.channel.recv_exit_status()

# Check if already authorized
stdin2, stdout2, stderr2 = client.exec_command(f"grep '{pubkey}' ~/.ssh/authorized_keys 2>/dev/null || echo 'NOT_FOUND'")
existing = stdout2.read().decode().strip()

if existing != "NOT_FOUND":
    print("Key already authorized")
else:
    stdin3, stdout3, stderr3 = client.exec_command(f"echo '{pubkey}' >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys")
    stdout3.channel.recv_exit_status()
    print("Key installed")

client.close()
