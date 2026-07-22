import paramiko
import os

HOST = '62.217.183.95'
USER = 'root'
PASS = '8884&JKL%f75'
LOCAL = r'D:\project\FRS_TEST'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username=USER, password=PASS, timeout=15)
sftp = ssh.open_sftp()

local_files = {
    'data/test_dataset.csv': '/opt/analytics/data/test_dataset.csv',
    'install_airflow.sh': '/opt/analytics/install_airflow.sh',
}

for local_rel, remote_abs in local_files.items():
    local_path = os.path.join(LOCAL, local_rel)
    sftp.put(local_path, remote_abs)
    print(f'Copied {local_rel} -> {remote_abs}')

sftp.close()
ssh.close()
print('All files synced.')
