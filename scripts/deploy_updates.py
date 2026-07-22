import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=10)

# Upload updated DAG
sftp = ssh.open_sftp()
sftp.put(r'D:\project\FRS_TEST\airflow\dags\anomaly_etl.py', '/opt/analytics/dags/anomaly_etl.py')
sftp.close()
print('DAG uploaded to server')

# Deploy view SQL and grant script to server too (for future reference)
sftp2 = ssh.open_sftp()
sftp2.put(r'D:\project\FRS_TEST\scripts\ddl.sql', '/opt/analytics/scripts/ddl.sql')
sftp2.close()
print('DDL uploaded')

ssh.close()
