import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', port=22, username='root', password='8884&JKL%f75', timeout=10)

# Deploy updated DAG to server
sftp = ssh.open_sftp()
sftp.put(r'D:\project\FRS_TEST\airflow\dags\anomaly_etl.py', '/opt/analytics/dags/anomaly_etl.py')
sftp.close()
print('DAG deployed to server')

# Copy to repo and commit
import os
repo = r'D:\project\FRS_TEST\vectornode-analytics\airflow\dags'
os.makedirs(os.path.dirname(repo), exist_ok=True)
import shutil
shutil.copy(r'D:\project\FRS_TEST\airflow\dags\anomaly_etl.py', repo + r'\anomaly_etl.py')
print('DAG copied to repo')

ssh.close()
