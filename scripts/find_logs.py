import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

# Find the actual log file
cmd = 'find /opt/analytics/logs -name "*.log" -type f 2>/dev/null | head -5'
stdin, stdout, stderr = ssh.exec_command(cmd)
log_files = stdout.read().decode(errors='replace').strip()
print(f'Log files: {log_files}')

# If no logs, check if the dir exists
cmd2 = 'ls -la /opt/analytics/logs/ 2>/dev/null || echo "no logs dir"'
stdin2, stdout2, stderr2 = ssh.exec_command(cmd2)
print(f'Log dir: {stdout2.read().decode(errors="replace").strip()}')

# Check scheduler logs for details about the failure
cmd3 = 'journalctl -u airflow-scheduler --no-pager -n 20 --output=short-precise 2>&1 | tail -20'
stdin3, stdout3, stderr3 = ssh.exec_command(cmd3)
print(f'Scheduler recent: {stdout3.read().decode(errors="replace").strip()[:1500]}')

ssh.close()
