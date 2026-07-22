import paramiko, time
s = paramiko.SSHClient()
s.set_missing_host_key_policy(paramiko.AutoAddPolicy())
s.connect('62.217.183.95', port=22, username='root', password='8884&JKL%f75', timeout=10)

sftp = s.open_sftp()
for f in ['tab_groups.py', 'tab_anomalies.py', 'tab_hypotheses.py']:
    sftp.put(r'D:\project\FRS_TEST\dashboard\pages\\' + f, '/opt/analytics/dashboard/pages/' + f)
    print(f'  {f}')
sftp.close()

stdin, stdout, stderr = s.exec_command('systemctl restart streamlit-dashboard')
stdout.read()
time.sleep(5)

stdin2, stdout2, stderr2 = s.exec_command('curl -s http://127.0.0.1:8501/_stcore/health')
print('Health:', stdout2.read().decode())

s.close()
