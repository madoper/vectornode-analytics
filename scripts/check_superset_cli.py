import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

cmds = [
    'docker exec podft-superset superset import_dashboards --help 2>&1 | head -5',
    'docker exec podft-superset sh -c "which superset && superset --help 2>&1 | head -10"',
    'docker exec podft-superset sh -c "ls /app/superset/bin/ 2>/dev/null; which flask 2>/dev/null; echo ---; python -c \"from flask import current_app; print(\\\"flask ok\\\")\" 2>/dev/null"',
]

for cmd in cmds:
    print(f'> {cmd[:80]}')
    stdin, stdout, stderr = ssh.exec_command(cmd)
    print(stdout.read().decode(errors='replace').strip()[:500])

ssh.close()
