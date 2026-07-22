import paramiko, json
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', port=22, username='root', password='8884&JKL%f75', timeout=10)

_, o, _ = ssh.exec_command(
    "docker exec podft-postgres psql -U podft -d superset -t -A -c "
    "\"SELECT query_context FROM slices WHERE id = 1\""
)
qc_raw = o.read().decode(errors='replace').strip()
print('Chart 1 QC:')
print(qc_raw[:1000])
print('...')
print(qc_raw[-500:])

ssh.close()
