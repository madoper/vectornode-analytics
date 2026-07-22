-- Create dataset for v_company_dashboard if not exists
INSERT INTO tables (table_name, database_id, schema, sql, created_on, changed_on, created_by_fk)
SELECT 'v_company_dashboard', 1, 'analytics', NULL, NOW(), NOW(), 1
WHERE NOT EXISTS (SELECT 1 FROM tables WHERE table_name = 'v_company_dashboard' AND database_id = 1);

-- Create dashboard
INSERT INTO dashboards (dashboard_title, slug, position_json, created_on, changed_on, created_by_fk, published)
VALUES ('VectorNode: anomalii i ekonomicheskie signaly', 'vectornode-anomalies', '{}', NOW(), NOW(), 1, true);

UPDATE dashboards SET description = 'Dashboard of anomalies and economic signals based on test_dataset.csv' WHERE slug = 'vectornode-anomalies';
