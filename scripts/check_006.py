import paramiko, time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

time.sleep(30)

# Check task log
cmd = 'tail -10 /opt/analytics/logs/dag_id=vectornode_anomaly_etl/run_id=manual_006/task_id=load_raw/attempt=1.log 2>&1'
stdin, stdout, stderr = ssh.exec_command(cmd)
print('Load_raw log:')
print(stdout.read().decode(errors='replace').strip()[:500])

# Check data
stdin2, stdout2, stderr2 = ssh.exec_command("docker exec podft-postgres psql -U podft -d analytics -c \"SELECT COUNT(*) FROM staging.test_dataset\" 2>&1 | tail -3")
print('\nStaging:', stdout2.read().decode(errors='replace').strip())

stdin3, stdout3, stderr3 = ssh.exec_command("docker exec podft-postgres psql -U podft -d analytics -c \"SELECT COUNT(*) FROM analytics.company\" 2>&1 | tail -3")
print('Company:', stdout3.read().decode(errors='replace').strip())

stdin4, stdout4, stderr4 = ssh.exec_command("docker exec podft-postgres psql -U podft -d analytics -c \"SELECT COUNT(*) FROM analytics.company_year\" 2>&1 | tail -3")
print('Company_year:', stdout4.read().decode(errors='replace').strip())

ssh.close()
