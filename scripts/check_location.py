import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=10)

stdin, stdout, stderr = ssh.exec_command(
    'curl -s -i -k "https://bi.vectornode.ru/api/v1/chart/data?form_data=%7B%22slice_id%22%3A1%7D" 2>&1 | head -15'
)
resp = stdout.read().decode(errors='replace').strip()
for line in resp.split('\n')[:10]:
    print(line[:250])

ssh.close()
