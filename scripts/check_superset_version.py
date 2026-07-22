import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', port=22, username='root', password='8884&JKL%f75', timeout=10)

# Check version
cmd = 'docker exec podft-superset pip show apache-superset 2>/dev/null | grep -E "^(Name|Version)"'
_, o, _ = ssh.exec_command(cmd)
print('pip:', o.read().decode(errors='replace'))

# Check the actual superset package
cmd2 = 'docker exec podft-superset python3 -c "import superset; print(dir(superset))" 2>/dev/null | tr "," "\n" | grep version'
_, o2, _ = ssh.exec_command(cmd2)
print('version attrs:', o2.read().decode(errors='replace'))

# Check what chart data API looks like
cmd3 = 'docker exec podft-superset grep -n "def data\|def create\|def post\|form_data\|slice_id" /app/superset/charts/data/api.py 2>/dev/null | head -20'
_, o3, _ = ssh.exec_command(cmd3)
print('API methods:', o3.read().decode(errors='replace'))

# Check the frontend version via the built files
cmd4 = 'docker exec podft-superset cat /app/superset/static/assets/version_info.json 2>/dev/null || echo NO_JSON'
_, o4, _ = ssh.exec_command(cmd4)
print('Frontend version:', o4.read().decode(errors='replace')[:200])

ssh.close()
