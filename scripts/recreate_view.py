import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

with open(r'D:\project\FRS_TEST\scripts\ddl.sql', 'r') as f:
    ddl = f.read()

# Extract only the CREATE VIEW part
view_start = ddl.find('CREATE OR REPLACE VIEW analytics.v_company_dashboard')
if view_start > 0:
    create_view_sql = ddl[view_start:]
    
    # Write to server and execute
    sftp2 = ssh.open_sftp()
    with sftp2.open('/tmp/create_view.sql', 'w') as f:
        f.write(create_view_sql.encode())
    sftp2.close()
    print('SQL written to server')
    
    stdin, stdout, stderr = ssh.exec_command(
        'docker exec -i podft-postgres psql -U podft -d analytics < /tmp/create_view.sql 2>&1'
    )
    print(stdout.read().decode(errors='replace').strip())
    
    # Verify
    stdin2, stdout2, stderr2 = ssh.exec_command(
        "docker exec podft-postgres psql -U podft -d analytics -c \"SELECT 'view exists' AS status FROM information_schema.tables WHERE table_schema='analytics' AND table_name='v_company_dashboard'\" 2>&1"
    )
    print(f'\nVerified: {stdout2.read().decode(errors="replace").strip()[:200]}')

ssh.close()
