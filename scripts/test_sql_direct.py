import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

cmds = [
    "docker exec podft-postgres psql -U podft -d analytics -c \"CREATE SCHEMA IF NOT EXISTS staging\" 2>&1",
    "docker exec podft-postgres psql -U podft -d analytics -c \"DROP TABLE IF EXISTS staging.test_dataset CASCADE\" 2>&1",
    "docker exec podft-postgres psql -U podft -d analytics -c \"CREATE TABLE staging.test_dataset (company_id TEXT, year BIGINT)\" 2>&1",
    "docker exec podft-postgres psql -U podft -d analytics -c \"SELECT COUNT(*) FROM staging.test_dataset\" 2>&1",
    "docker exec podft-postgres psql -U podft -d analytics -c \"\\dt staging.*\" 2>&1",
]

for desc, cmd in [("Create schema", cmds[0]), ("Drop table", cmds[1]), ("Create table", cmds[2]), ("Select", cmds[3]), ("List tables", cmds[4])]:
    stdin, stdout, stderr = ssh.exec_command(cmd)
    print(f'{desc}: {stdout.read().decode(errors="replace").strip()[:200]}')

ssh.close()
