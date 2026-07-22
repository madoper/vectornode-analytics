import paramiko, time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

time.sleep(30)

# Check all tables
for tbl in ["analytics.company", "analytics.company_year",
            "analytics.company_features", "analytics.company_growth",
            "analytics.company_zscore", "analytics.anomaly"]:
    stdin, stdout, stderr = ssh.exec_command(f"docker exec podft-postgres psql -U podft -d analytics -c \"SELECT COUNT(*) FROM {tbl}\" 2>&1")
    res = stdout.read().decode(errors='replace').strip()
    for line in res.split('\n'):
        if line.strip().isdigit():
            print(f'{tbl:35s} {line.strip()}')
            break

# Anomaly breakdown
stdin2, stdout2, stderr2 = ssh.exec_command("docker exec podft-postgres psql -U podft -d analytics -c \"SELECT criticality, COUNT(*) FROM analytics.anomaly GROUP BY criticality ORDER BY criticality\" 2>&1")
print('\nAnomalies:')
print(stdout2.read().decode(errors='replace').strip())

ssh.close()
