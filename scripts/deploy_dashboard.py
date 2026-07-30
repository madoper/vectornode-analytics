import paramiko, os, sys

HOST = '62.217.183.95'
USER = 'root'
PWD = '8884&JKL%f75'
LOCAL = r'D:\project\FRS_TEST\dashboard'
REMOTE = '/opt/analytics/dashboard'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username=USER, password=PWD, timeout=30, look_for_keys=False, allow_agent=False)

sftp = ssh.open_sftp()

for root, dirs, files in os.walk(LOCAL):
    rel = os.path.relpath(root, LOCAL)
    remote_dir = os.path.join(REMOTE, rel).replace('\\', '/')
    try:
        sftp.stat(remote_dir)
    except FileNotFoundError:
        sftp.mkdir(remote_dir)
        print(f'MKDIR {remote_dir}')
    for f in files:
        local_path = os.path.join(root, f)
        remote_path = os.path.join(remote_dir, f).replace('\\', '/')
        sftp.put(local_path, remote_path)
        print(f'PUT {remote_path}')

sftp.close()

cmd = (
    "kill -9 $(ps aux | grep 'streamlit run' | grep -v grep | awk '{print $2}') 2>/dev/null; "
    "sleep 2; "
    "cd /opt/analytics/dashboard && "
    "setsid /opt/analytics/venv/bin/streamlit run app.py "
    "--server.port 8501 --server.address 127.0.0.1 --server.headless true "
    ">/dev/null 2>&1 & "
    "sleep 3; "
    "ps aux | grep -v grep | grep streamlit"
)

stdin, stdout, stderr = ssh.exec_command(cmd, timeout=15)
print('\nRESTART RESULT:')
print(stdout.read().decode())
err = stderr.read().decode()
if err:
    print(f'STDERR: {err}')
ssh.close()
print('DONE')
