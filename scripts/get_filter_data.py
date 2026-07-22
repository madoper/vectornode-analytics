import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', port=22, username='root', password='8884&JKL%f75', timeout=10)

# Get the full filter state entry (entry #5)
cmd = "docker exec podft-postgres psql -U podft -d superset -t -A -c \"SELECT encode(value, 'escape') FROM key_value WHERE id = 5\""
_, o, _ = ssh.exec_command(cmd)
raw = o.read().decode(errors='replace').strip()
print('Entry #5 raw:')
print(raw[:2000])

# Also check how the chart command uses dashboard_id for filter context
cmd2 = "docker exec podft-superset grep -rn 'dashboard_id\\|filter_state\\|extra_filters\\|native_filter' /app/superset/commands/chart_data.py 2>/dev/null | head -20"
_, o2, _ = ssh.exec_command(cmd2)
print('\nChart data command filter handling:')
print(o2.read().decode(errors='replace'))

ssh.close()
