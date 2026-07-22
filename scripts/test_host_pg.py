import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

cmds = [
    # Test host connection to Docker PostgreSQL
    'apt list --installed 2>/dev/null | grep postgresql-client || apt install -y postgresql-client -q',
    'PGPASSWORD=airflow_pass psql -h localhost -p 5432 -U airflow_user -d airflow_db -c "SELECT current_user, current_database()"',
    'PGPASSWORD=dbt_pass psql -h localhost -p 5432 -U dbt_user -d analytics -c "SELECT current_user, current_database()"',
]

for cmd in cmds:
    print('=== ' + cmd + ' ===')
    stdin, stdout, stderr = ssh.exec_command(cmd)
    print(stdout.read().decode().strip())
    err = stderr.read().decode().strip()
    if err:
        print('STDERR:', err)

ssh.close()
