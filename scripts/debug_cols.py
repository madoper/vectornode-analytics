import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

# Get raw column output
stdin, stdout, stderr = ssh.exec_command(
    "docker exec podft-postgres psql -U podft -d analytics -c "
    "\"SELECT column_name, data_type FROM information_schema.columns WHERE table_schema='analytics' AND table_name='v_company_dashboard' ORDER BY ordinal_position\" 2>&1"
)
print('Raw output:')
out = stdout.read().decode(errors='replace').strip()
print(out[:1000])

ssh.close()
