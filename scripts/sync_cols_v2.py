import paramiko, base64

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

# Step 1: Get columns from analytics.v_company_dashboard
stdin, stdout, stderr = ssh.exec_command(
    "docker exec podft-postgres psql -U podft -d analytics -t -A -F '\t' "
    "-c \"SELECT column_name, data_type FROM information_schema.columns WHERE table_schema='analytics' AND table_name='v_company_dashboard' ORDER BY ordinal_position\" 2>&1"
)
raw_cols = stdout.read().decode(errors='replace').strip()
print('Raw columns received')

# Parse columns
cols = []
for line in raw_cols.split('\n'):
    line = line.strip()
    if '\t' in line:
        name, dtype = line.split('\t', 1)
        cols.append((name.strip(), dtype.strip()))

print(f'Found {len(cols)} columns')

# Step 2: Generate INSERT SQL
now = "NOW()"
inserts = []
for col_name, col_type in cols:
    if col_type in ('integer', 'bigint'):
        sql_type = 'BIGINT'
    elif col_type in ('numeric', 'double precision', 'real'):
        sql_type = 'DOUBLE PRECISION'
    elif col_type == 'timestamp with time zone':
        sql_type = 'TIMESTAMP'
    else:
        sql_type = 'VARCHAR(255)'
    
    is_dttm = 'true' if col_name in ('year', 'detected_at', 'computed_at', 'processed_at') else 'false'
    
    inserts.append(
        f"INSERT INTO table_columns (table_id, column_name, type, is_dttm, is_active, groupby, filterable, created_on, changed_on) "
        f"SELECT 3, '{col_name}', '{sql_type}', {is_dttm}, true, true, true, {now}, {now} "
        f"WHERE NOT EXISTS (SELECT 1 FROM table_columns WHERE table_id=3 AND column_name='{col_name}');"
    )

# Step 3: Execute via base64 to avoid quoting issues
full_sql = '\n'.join(inserts)
sql_b64 = base64.b64encode(full_sql.encode()).decode()

stdin2, stdout2, stderr2 = ssh.exec_command(
    f'echo {sql_b64} | base64 -d | docker exec -i podft-postgres psql -U podft -d superset 2>&1'
)
result = stdout2.read().decode(errors='replace').strip()
print(f'Insert result: {result[:500]}')

# Verify
stdin3, stdout3, stderr3 = ssh.exec_command(
    "docker exec podft-postgres psql -U podft -d superset -c \"SELECT COUNT(*) FROM table_columns WHERE table_id=3\" 2>&1"
)
result3 = stdout3.read().decode(errors='replace').strip()
print(f'Total columns: {result3}')

ssh.close()
