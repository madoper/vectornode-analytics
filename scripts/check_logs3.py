import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=10)

_, o, _ = ssh.exec_command(
    'cat /opt/analytics/logs/dag_id=vectornode_anomaly_etl/run_id=full_data_001/task_id=build_group_signals/attempt=1.log'
)
print(o.read().decode(errors='replace'))
ssh.close()
