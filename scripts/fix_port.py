import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

# Fix port in airflow.cfg
stdin, stdout, stderr = ssh.exec_command(
    'cat /opt/analytics/airflow.cfg | grep -n "web_server_port" || echo "NOT_FOUND"'
)
cfg_result = stdout.read().decode(errors='replace').strip()
print('Current cfg port setting:', cfg_result)

# Read and fix airflow.cfg
sftp2 = ssh.open_sftp()
with sftp2.open('/opt/analytics/airflow.cfg', 'r') as f:
    cfg_content = f.read().decode(errors='replace')

cfg_content = cfg_content.replace('web_server_port = 8080', 'web_server_port = 8081')

with sftp2.open('/opt/analytics/airflow.cfg', 'w') as f:
    f.write(cfg_content.encode())
sftp2.close()
print('Fixed airflow.cfg port to 8081')

# Rewrite service file with port 8081
service_content = '''[Unit]
Description=Apache Airflow Webserver
After=network.target podft-postgres.service
Wants=podft-postgres.service

[Service]
Type=simple
User=root
Group=root
Environment="AIRFLOW_HOME=/opt/analytics"
Environment="PATH=/opt/analytics/venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
Environment="AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=postgresql+psycopg2://airflow_user:airflow_pass@localhost:5432/airflow_db"
Environment="AIRFLOW__CORE__EXECUTOR=SequentialExecutor"
Environment="AIRFLOW__CORE__LOAD_EXAMPLES=False"
Environment="AIRFLOW__CORE__DAGS_FOLDER=/opt/analytics/dags"
Environment="AIRFLOW__WEBSERVER__WEB_SERVER_PORT=8081"
Environment="AIRFLOW__WEBSERVER__EXPOSE_CONFIG=True"
ExecStart=/opt/analytics/venv/bin/airflow webserver
Restart=on-failure
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
'''

sftp = ssh.open_sftp()
with sftp.open('/etc/systemd/system/airflow-webserver.service', 'w') as f:
    f.write(service_content.encode())
sftp.close()

cmds = [
    'systemctl daemon-reload',
    'systemctl stop airflow-webserver 2>/dev/null; systemctl start airflow-webserver 2>&1',
    'sleep 3',
    'systemctl show -p ActiveState airflow-webserver',
    'journalctl -u airflow-webserver --no-pager -n 5 --output=short-precise 2>&1',
    'ss -tlnp | grep 8081',
]

for cmd in cmds:
    print(f'> {cmd}')
    stdin, stdout, stderr = ssh.exec_command(cmd)
    print(stdout.read().decode(errors='replace').strip())

ssh.close()
