import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

cmds = [
    # Reset passwords for airflow_user and dbt_user
    'docker exec podft-postgres psql -U podft -c "ALTER USER airflow_user WITH PASSWORD \'airflow_pass\';"',
    'docker exec podft-postgres psql -U podft -c "ALTER USER dbt_user WITH PASSWORD \'dbt_pass\';"',
    # Add trust for Docker network (172.0.0.0/8)
    'docker exec podft-postgres sh -c "echo \'host all all 172.0.0.0/8 trust\' >> /var/lib/postgresql/data/pg_hba.conf"',
    # Reload config
    'docker exec podft-postgres psql -U podft -c "SELECT pg_reload_conf();"',
]

for cmd in cmds:
    print('=== ' + cmd + ' ===')
    stdin, stdout, stderr = ssh.exec_command(cmd)
    print(stdout.read().decode().strip())
    err = stderr.read().decode().strip()
    if err:
        print('STDERR:', err)
    rc = stdout.channel.recv_exit_status()
    print('exit:', rc)

ssh.close()
