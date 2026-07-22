import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=10)

# Set search_path for podft user to include analytics
sqls = [
    "ALTER USER podft SET search_path = public, analytics",
    "SHOW search_path",
]
for s in sqls:
    _, o, _ = ssh.exec_command(f'docker exec podft-postgres psql -U podft -d analytics -c "{s}"')
    print(o.read().decode(errors='replace'))

print('---')

# Now create the view
with open(r'D:\project\FRS_TEST\scripts\ddl.sql', 'r') as f:
    ddl = f.read()

# Extract only the CREATE VIEW part (from line 120 onwards)
view_sql = """CREATE OR REPLACE VIEW analytics.v_company_dashboard AS
SELECT
    c.company_id,
    c.company_name,
    c.inn,
    c.ogrn_year,
    c.region,
    c.okved_code,
    c.okved_section,
    c.founder_id,
    c.address_hash,
    cy.year,
    cy.revenue,
    cy.cost_of_goods,
    cy.gross_profit,
    cy.opex,
    cy.operating_profit,
    cy.net_profit,
    cy.taxes_paid,
    cy.headcount,
    cy.payroll_fund,
    cy.dividends_paid,
    cf.net_margin,
    cf.gross_margin,
    cf.operating_margin,
    cf.rev_per_emp,
    cf.profit_per_emp,
    cf.payroll_per_emp,
    cf.tax_to_profit,
    cf.payout_ratio,
    cf.financial_pressure_ratio,
    cf.company_age,
    cg.rev_growth,
    cg.profit_growth,
    cg.emp_growth,
    cg.payroll_growth,
    z_net_margin.zscore     AS net_margin_zscore,
    z_rev_per_emp.zscore    AS rev_per_emp_zscore,
    z_fin_pressure.zscore   AS financial_pressure_zscore,
    z_rev_growth.zscore     AS rev_growth_zscore,
    z_emp_growth.zscore     AS emp_growth_zscore,
    a.hypothesis_code,
    a.metric,
    a.value,
    a.zscore AS anomaly_zscore,
    a.interpretation,
    a.interpretation_reason,
    a.criticality,
    a.criticality_score
FROM analytics.company c
JOIN analytics.company_year cy
  ON cy.company_id = c.company_id
LEFT JOIN analytics.company_features cf
  ON cf.company_id = cy.company_id AND cf.year = cy.year
LEFT JOIN analytics.company_growth cg
  ON cg.company_id = cy.company_id AND cg.year = cy.year
LEFT JOIN analytics.company_zscore z_net_margin
  ON z_net_margin.company_id = cy.company_id AND z_net_margin.year = cy.year
 AND z_net_margin.metric = 'net_margin'
LEFT JOIN analytics.company_zscore z_rev_per_emp
  ON z_rev_per_emp.company_id = cy.company_id AND z_rev_per_emp.year = cy.year
 AND z_rev_per_emp.metric = 'rev_per_emp'
LEFT JOIN analytics.company_zscore z_fin_pressure
  ON z_fin_pressure.company_id = cy.company_id AND z_fin_pressure.year = cy.year
 AND z_fin_pressure.metric = 'financial_pressure_ratio'
LEFT JOIN analytics.company_zscore z_rev_growth
  ON z_rev_growth.company_id = cy.company_id AND z_rev_growth.year = cy.year
 AND z_rev_growth.metric = 'rev_growth'
LEFT JOIN analytics.company_zscore z_emp_growth
  ON z_emp_growth.company_id = cy.company_id AND z_emp_growth.year = cy.year
 AND z_emp_growth.metric = 'emp_growth'
LEFT JOIN analytics.anomaly a
  ON a.company_id = cy.company_id AND a.year = cy.year"""

# Write the SQL to a temp file on server and execute
import base64
encoded = base64.b64encode(view_sql.encode()).decode()

_, o, _ = ssh.exec_command(f'echo {encoded} | base64 -d | docker exec -i podft-postgres psql -U podft -d analytics')
print(o.read().decode(errors='replace'))

# Verify
_, o2, _ = ssh.exec_command('docker exec podft-postgres psql -U podft -d analytics -c "SELECT COUNT(*) FROM analytics.v_company_dashboard"')
print('\nView row count:')
print(o2.read().decode(errors='replace'))

ssh.close()
