import paramiko, os
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', port=22, username='root', password='8884&JKL%f75', timeout=15)

sftp = ssh.open_sftp()

# Create directory structure
base = '/opt/analytics/dashboard'
for d in ['', '/utils', '/pages']:
    try:
        sftp.mkdir(base + d)
    except:
        pass

# Upload all files
local_base = r'D:\project\FRS_TEST\dashboard'
for root, dirs, files in os.walk(local_base):
    for fname in files:
        local_path = os.path.join(root, fname)
        rel_path = os.path.relpath(local_path, local_base).replace('\\', '/')
        remote_path = f'{base}/{rel_path}'
        sftp.put(local_path, remote_path)
        print(f'  Uploaded: {rel_path}')

sftp.close()

# Install deps and start streamlit
_, o, _ = ssh.exec_command(
    f'/opt/analytics/venv/bin/python -m pip install streamlit plotly sqlalchemy psycopg2-binary 2>&1 | tail -3'
)
out = o.read()
print(f'\nPip: {len(out)} bytes')

# Create systemd service
service = """[Unit]
Description=Streamlit Analytics Dashboard
After=network.target

[Service]
User=root
WorkingDirectory=/opt/analytics/dashboard
ExecStart=/opt/analytics/venv/bin/streamlit run app.py --server.port 8501 --server.address 127.0.0.1 --server.headless true
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
"""

sftp2 = ssh.open_sftp()
f = sftp2.file('/etc/systemd/system/streamlit-dashboard.service', 'w')
f.write(service)
f.close()
sftp2.close()

# Enable and start
_, o2, _ = ssh.exec_command('systemctl daemon-reload && systemctl enable streamlit-dashboard && systemctl restart streamlit-dashboard 2>&1')
print('Service:', o2.read().decode(errors='replace').strip())

# Check status
import time
time.sleep(5)
_, o3, _ = ssh.exec_command('systemctl status streamlit-dashboard --no-pager 2>&1 | head -10')
print('Status:', o3.read().decode(errors='replace')[:400])

ssh.close()
