import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)
sftp = ssh.open_sftp()
sftp.put(r'D:\project\FRS_TEST\dbt\models\marts\company_risk_summary.sql', '/opt/analytics/analytics_dbt/models/marts/company_risk_summary.sql')
sftp.put(r'D:\project\FRS_TEST\dbt\models\staging\stg_anomalies.sql', '/opt/analytics/analytics_dbt/models/staging/stg_anomalies.sql')
sftp.close()

cmd = (
    'cd /opt/analytics/analytics_dbt && '
    '. /opt/analytics/venv/bin/activate && '
    'dbt run --profiles-dir . --project-dir . 2>&1'
)

stdin, stdout, stderr = ssh.exec_command(cmd)
print(stdout.read().decode(errors='replace'))
ssh.close()
