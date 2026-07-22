import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', port=22, username='root', password='8884&JKL%f75', timeout=10)

sqls = [
    # Step 1: Create materialized table from view
    ("CREATE TABLE analytics.v_company_dashboard_new AS SELECT * FROM analytics.v_company_dashboard", "Create materialized table"),
    # Step 2: Drop the view
    ("DROP VIEW IF EXISTS analytics.v_company_dashboard CASCADE", "Drop view"),
    # Step 3: Rename table to view's name
    ("ALTER TABLE analytics.v_company_dashboard_new RENAME TO v_company_dashboard", "Rename table"),
    # Step 4: Add indexes
    ("CREATE INDEX IF NOT EXISTS idx_v_dash_company ON analytics.v_company_dashboard(company_id)", "Index company_id"),
    ("CREATE INDEX IF NOT EXISTS idx_v_dash_year ON analytics.v_company_dashboard(year)", "Index year"),
    ("CREATE INDEX IF NOT EXISTS idx_v_dash_criticality ON analytics.v_company_dashboard(criticality)", "Index criticality"),
    # Step 5: Grant permissions
    ("GRANT SELECT ON analytics.v_company_dashboard TO PUBLIC", "Grant SELECT"),
    # Step 6: Verify row count
    ("SELECT COUNT(*) AS rows FROM analytics.v_company_dashboard", "Verify rows"),
]

for sql, desc in sqls:
    _, o, _ = ssh.exec_command(f'docker exec podft-postgres psql -U podft -d analytics -c "{sql}"')
    out = o.read().decode(errors='replace')
    print(f'{desc}:')
    print(out.strip()[:300])
    print('---')

ssh.close()
