import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

# Get columns from the view and insert into superset table_columns
sql = """
INSERT INTO table_columns (table_id, column_name, "type", is_dttm, is_active, groupby, filterable, "expression", created_on, changed_on)
SELECT 3, column_name, 
  CASE 
    WHEN data_type IN ('integer', 'bigint') THEN 'BIGINT'
    WHEN data_type IN ('numeric', 'double precision', 'real') THEN 'DOUBLE PRECISION'
    WHEN data_type = 'timestamp with time zone' THEN 'TIMESTAMP'
    ELSE 'VARCHAR(255)'
  END,
  CASE WHEN column_name IN ('year') THEN true ELSE false END,
  true, true, true, NULL, NOW(), NOW()
FROM information_schema.columns 
WHERE table_schema = 'analytics' AND table_name = 'v_company_dashboard'
AND NOT EXISTS (SELECT 1 FROM superset.public.table_columns tc WHERE tc.table_id = 3 AND tc.column_name = information_schema.columns.column_name)
ON CONFLICT DO NOTHING;
"""

# Write the SQL and execute via docker
stdin, stdout, stderr = ssh.exec_command(
    f"docker exec -i podft-postgres psql -U podft -d superset -c \"{sql}\" 2>&1"
)
res = stdout.read().decode(errors='replace').strip()
print('Insert result:', res[:200])

# Check column count
stdin2, stdout2, stderr2 = ssh.exec_command(
    "docker exec podft-postgres psql -U podft -d superset -c \"SELECT COUNT(*) FROM table_columns WHERE table_id=3\" 2>&1"
)
print('Columns:', stdout2.read().decode(errors='replace').strip())

ssh.close()
