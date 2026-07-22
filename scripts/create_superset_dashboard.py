import paramiko, json

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

# Create dashboard in Superset metadata database

sql = """
-- Create dataset for v_company_dashboard if not exists
INSERT INTO tables (table_name, database_id, schema, sql, created_on, changed_on, created_by_fk)
SELECT 'v_company_dashboard', 1, 'analytics', NULL, NOW(), NOW(), 1
WHERE NOT EXISTS (SELECT 1 FROM tables WHERE table_name = 'v_company_dashboard' AND database_id = 1);

-- Get the table ID
DO $$
DECLARE
    tbl_id INTEGER;
    dash_id INTEGER;
    slice_id INTEGER;
BEGIN
    SELECT id INTO tbl_id FROM tables WHERE table_name = 'v_company_dashboard' AND database_id = 1;
    
    IF tbl_id IS NULL THEN
        RAISE NOTICE 'Table not found, creating';
        INSERT INTO tables (table_name, database_id, schema, created_on, changed_on, created_by_fk)
        VALUES ('v_company_dashboard', 1, 'analytics', NOW(), NOW(), 1)
        RETURNING id INTO tbl_id;
    END IF;

    -- Create dashboard
    INSERT INTO dashboards (dashboard_title, slug, position_json, created_on, changed_on, created_by_fk, published)
    VALUES ('VectorNode: аномалии и экономические сигналы', 'vectornode-anomalies', '{}', NOW(), NOW(), 1, true)
    RETURNING id INTO dash_id;

    -- Update description
    UPDATE dashboards SET description = 'Дашборд аномалий и экономических сигналов на основе данных test_dataset.csv' WHERE id = dash_id;

    RAISE NOTICE 'Dashboard created with id: %', dash_id;
END $$;
"""

# Execute in single transaction
stdin, stdout, stderr = ssh.exec_command(
    f'docker exec -i podft-postgres psql -U podft -d superset -c "{sql}" 2>&1'
)
print(stdout.read().decode(errors='replace').strip()[:500])

# Verify
stdin2, stdout2, stderr2 = ssh.exec_command(
    "docker exec podft-postgres psql -U podft -d superset -c \"SELECT id, dashboard_title, published FROM dashboards ORDER BY id DESC LIMIT 3\" 2>&1"
)
print('\nDashboards:')
print(stdout2.read().decode(errors='replace').strip())

ssh.close()
