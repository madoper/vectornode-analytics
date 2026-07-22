import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

sftp = ssh.open_sftp()
with sftp.open('/etc/nginx/sites-enabled/vectornode.ru', 'r') as f:
    cfg = f.read().decode('utf-8', errors='replace')

# Add proxy_redirect to /login/ location
old_login = '''    location /login/ {
        proxy_pass http://127.0.0.1:8088/login/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Prefix /superset;
    }'''

new_login = '''    location /login/ {
        proxy_pass http://127.0.0.1:8088/login/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Prefix /superset;
        proxy_redirect / /superset/;
    }'''

cfg = cfg.replace(old_login, new_login)

# Add proxy_redirect to /logout/ location
old_logout = '''    location /logout/ {
        proxy_pass http://127.0.0.1:8088/logout/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Prefix /superset;
    }'''

new_logout = '''    location /logout/ {
        proxy_pass http://127.0.0.1:8088/logout/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Prefix /superset;
        proxy_redirect / /superset/;
    }'''

cfg = cfg.replace(old_logout, new_logout)

# Add proxy_redirect to /user_info/ location  
old_info = '''    location /user_info/ {
        proxy_pass http://127.0.0.1:8088/user_info/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Prefix /superset;
    }'''

new_info = '''    location /user_info/ {
        proxy_pass http://127.0.0.1:8088/user_info/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Prefix /superset;
        proxy_redirect / /superset/;
    }'''

cfg = cfg.replace(old_info, new_info)

with sftp.open('/etc/nginx/sites-enabled/vectornode.ru', 'w') as f:
    f.write(cfg.encode())
sftp.close()

stdin, stdout, stderr = ssh.exec_command('nginx -t 2>&1 && systemctl reload nginx 2>&1')
print('Nginx:', stdout.read().decode(errors='replace').strip())

# Test login flow
import time
time.sleep(2)

# Simulate login POST to /login/ - check redirect
stdin2, stdout2, stderr2 = ssh.exec_command(
    "curl -s -D - -o /dev/null -X POST https://vectornode.ru/login/ "
    "-d 'username=admin&password=admin' "
    "-H 'Content-Type: application/x-www-form-urlencoded' "
    "-H 'Referer: https://vectornode.ru/login/' 2>&1 | head -15"
)
print('\nLogin POST redirect:')
print(stdout2.read().decode(errors='replace').strip())

# Also test through API login to check cookies
stdin3, stdout3, stderr3 = ssh.exec_command(
    "curl -s -D - -o /dev/null -X POST https://vectornode.ru/superset/api/v1/security/login "
    "-H 'Content-Type: application/json' "
    "-d '{\"username\":\"admin\",\"password\":\"admin\",\"provider\":\"db\"}' 2>&1 | head -15"
)
print('\nAPI login response:')
print(stdout3.read().decode(errors='replace').strip())

# Check current Nginx section for /login/
stdin4, stdout4, stderr4 = ssh.exec_command(
    "grep -A 10 'location /login/' /etc/nginx/sites-enabled/vectornode.ru"
)
print('\n/login/ location:')
print(stdout4.read().decode(errors='replace').strip())

ssh.close()
