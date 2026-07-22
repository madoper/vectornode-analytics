import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=10)

for sql in [
    "SELECT COUNT(*) AS cnt FROM analytics.company",
    "SELECT COUNT(*) AS cnt FROM analytics.company_year",
    "SELECT criticality, COUNT(*) AS cnt FROM analytics.anomaly GROUP BY criticality ORDER BY criticality",
    "SELECT interpretation, COUNT(*) AS cnt FROM analytics.anomaly GROUP BY interpretation ORDER BY interpretation",
    "SELECT hypothesis_code, COUNT(*) AS cnt FROM analytics.anomaly GROUP BY hypothesis_code ORDER BY hypothesis_code",
]:
    stdin, stdout, stderr = ssh.exec_command(f"docker exec podft-postgres psql -U podft -d analytics -c \"{sql}\" 2>&1 | tail -10")
    print(stdout.read().decode(errors='replace').strip())
    print()

ssh.close()
