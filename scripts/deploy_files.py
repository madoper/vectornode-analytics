import paramiko, os

HOST = '62.217.183.95'
USER = 'root'
PASS = '8884&JKL%f75'
LOCAL = r'D:\project\FRS_TEST'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username=USER, password=PASS, timeout=15)

# First create directories
mkdirs = [
    'mkdir -p /opt/analytics/analytics_dbt/{models/staging,models/marts,target}',
]
for cmd in mkdirs:
    ssh.exec_command(cmd)

sftp = ssh.open_sftp()

files = [
    ('scripts/ml_anomaly_detection.py', '/opt/analytics/scripts/ml_anomaly_detection.py'),
    ('dags/analytics_dag.py', '/opt/analytics/dags/analytics_dag.py'),
    ('dbt/dbt_project.yml', '/opt/analytics/analytics_dbt/dbt_project.yml'),
    ('dbt/profiles.yml', '/opt/analytics/analytics_dbt/profiles.yml'),
    ('dbt/models/staging/stg_anomalies.sql', '/opt/analytics/analytics_dbt/models/staging/stg_anomalies.sql'),
    ('dbt/models/marts/company_risk_summary.sql', '/opt/analytics/analytics_dbt/models/marts/company_risk_summary.sql'),
    ('systemd/airflow-webserver.service', '/etc/systemd/system/airflow-webserver.service'),
    ('systemd/airflow-scheduler.service', '/etc/systemd/system/airflow-scheduler.service'),
]

for local_rel, remote_abs in files:
    local_path = os.path.join(LOCAL, local_rel)
    sftp.put(local_path, remote_abs)
    print(f'OK  {local_rel}')

sftp.close()

# Install dbt, enable services
cmds = [
    '. /opt/analytics/venv/bin/activate && pip install dbt-core dbt-postgres -q 2>&1 | tail -2',
    'systemctl daemon-reload',
    'systemctl enable airflow-webserver airflow-scheduler',
]

for cmd in cmds:
    print(f'--- {cmd[:60]}... ---')
    stdin, stdout, stderr = ssh.exec_command(cmd)
    out = stdout.read().decode().strip()
    if out:
        print(out)
    err = stderr.read().decode().strip()
    if err:
        print('ERR:', err)

ssh.close()
print('DONE')
