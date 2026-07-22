import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

# Get columns from the view
stdin, stdout, stderr = ssh.exec_command(
    "docker exec podft-postgres psql -U podft -d analytics -c "
    "\"SELECT column_name, data_type FROM information_schema.columns WHERE table_schema='analytics' AND table_name='v_company_dashboard' ORDER BY ordinal_position\" -A -t -F '|' 2>&1"
)
cols = stdout.read().decode(errors='replace').strip().split('\n')
print(f'Found {len(cols)} columns:')
for col in cols[:5]:
    print(f'  {col}')

# Insert columns into superset table_columns
insert_sql = """
INSERT INTO table_columns (table_id, column_name, type, is_dttm, is_active, groupby, filterable, created_on, changed_on)
SELECT 3, col_info[1], 
  CASE 
    WHEN col_info[2] LIKE '%%numeric%%' OR col_info[2] LIKE '%%int%%' OR col_info[2] LIKE '%%double%%' THEN 'DOUBLE PRECISION'
    ELSE 'VARCHAR(255)'
  END,
  false, true, true, true,
  NOW(), NOW()
FROM (
  SELECT string_to_array(column_data, '|') as col_info
  FROM (
    SELECT unnest(string_to_array($COLUMNS, E'\\n')) as column_data
  ) sub
) sub2
ON CONFLICT DO NOTHING;
"""

# Actually let me write a simpler approach - generate the SQL
stdin2, stdout2, stderr2 = ssh.exec_command(
    "docker exec podft-postgres psql -U podft -d analytics -t -A -F $'\\t' "
    "-c \"SELECT column_name, data_type FROM information_schema.columns WHERE table_schema='analytics' AND table_name='v_company_dashboard' ORDER BY ordinal_position\" 2>&1"
)
print('\nRaw columns:')
print(stdout2.read().decode(errors='replace').strip()[:1000])

ssh.close()
