import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=10)

cmds = [
    'docker exec podft-postgres psql -U podft -d analytics -c "SELECT DISTINCT year FROM company_year ORDER BY year"',
    'docker exec podft-postgres psql -U podft -d analytics -c "SELECT year, COUNT(*) AS cnt FROM company_year GROUP BY year ORDER BY year"',
    'docker exec podft-postgres psql -U podft -d analytics -c "SELECT year, COUNT(*) AS cnt FROM analytics.v_company_dashboard GROUP BY year ORDER BY year"',
    'docker exec podft-postgres psql -U podft -d analytics -c "SELECT year, COUNT(*) AS cnt FROM staging.test_dataset GROUP BY year ORDER BY year"',
]
for c in cmds:
    _, o, _ = ssh.exec_command(c)
    print(o.read().decode(errors='replace'))
    print('---')

ssh.close()
