import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=10)

cmds = [
    "GRANT USAGE ON SCHEMA analytics TO PUBLIC",
    "GRANT SELECT ON ALL TABLES IN SCHEMA analytics TO PUBLIC",
    "GRANT SELECT ON analytics.v_company_dashboard TO PUBLIC",
    "GRANT SELECT ON analytics.company TO PUBLIC",
    "GRANT SELECT ON analytics.company_year TO PUBLIC",
    "GRANT SELECT ON analytics.company_features TO PUBLIC",
    "GRANT SELECT ON analytics.company_growth TO PUBLIC",
    "GRANT SELECT ON analytics.company_zscore TO PUBLIC",
    "GRANT SELECT ON analytics.anomaly TO PUBLIC",
    "GRANT SELECT ON analytics.group_signal TO PUBLIC",
]

for c in cmds:
    cmd = f'docker exec podft-postgres psql -U podft -d analytics -c "{c}"'
    _, o, e = ssh.exec_command(cmd)
    print(c[:60], '->', o.read().decode(errors='replace').strip()[:100])

# Verify
_, o2, _ = ssh.exec_command(
    'docker exec podft-postgres psql -U podft -d analytics -c "SELECT schemaname, viewname, viewowner FROM pg_views WHERE viewname LIKE \'v_%\'"'
)
print('\nView:', o2.read().decode(errors='replace'))

ssh.close()
