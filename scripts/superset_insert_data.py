import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

sftp = ssh.open_sftp()
with sftp.open('/tmp/superset_insert.sql', 'w') as f:
    f.write(b"""
INSERT INTO tables (table_name, database_id, schema, sql, created_on, changed_on, created_by_fk)
VALUES 
  ('company_risk_summary', 1, 'public_marts', NULL, NOW(), NOW(), 1),
  ('anomalies_staging', 1, 'public', NULL, NOW(), NOW(), 1);

INSERT INTO dashboards (dashboard_title, slug, position_json, created_on, changed_on, created_by_fk, published)
VALUES ('Anomaly Detection Dashboard', 'anomaly-detection', '{}', NOW(), NOW(), 1, true);
""")
sftp.close()

stdin, stdout, stderr = ssh.exec_command(
    'docker exec -i podft-postgres psql -U podft -d superset < /tmp/superset_insert.sql 2>&1'
)
print(stdout.read().decode(errors='replace').strip())

# Verify
stdin2, stdout2, stderr2 = ssh.exec_command(
    'docker exec podft-postgres psql -U podft -d superset -c "SELECT id, table_name, database_id, schema FROM tables WHERE table_name LIKE \'%risk%\' OR table_name LIKE \'%anomaly%\'"'
)
print('\nTables:', stdout2.read().decode(errors='replace').strip())

stdin3, stdout3, stderr3 = ssh.exec_command(
    'docker exec podft-postgres psql -U podft -d superset -c "SELECT id, dashboard_title FROM dashboards"'
)
print('Dashboards:', stdout3.read().decode(errors='replace').strip())

ssh.close()
