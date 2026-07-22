import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

sftp = ssh.open_sftp()
with sftp.open('/etc/nginx/sites-enabled/vectornode.ru', 'r') as f:
    cfg = f.read().decode('utf-8', errors='replace')

old = '''    location /superset/ {
        proxy_pass http://127.0.0.1:8088/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $host;
        proxy_redirect / /superset/;
        proxy_request_buffering off;
        client_max_body_size 50m;
        proxy_connect_timeout 300s;
        proxy_read_timeout 300s;
        proxy_send_timeout 300s;
        sub_filter_once off;
        sub_filter_types text/html;
        sub_filter 'href="/static/' 'href="/superset/static/';
        sub_filter 'src="/static/' 'src="/superset/static/';
        sub_filter "if ('serviceWorker' in navigator)" "if (false)";
    }'''

new = '''    location /superset/ {
        proxy_pass http://127.0.0.1:8088/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header X-Forwarded-Prefix /superset;
        proxy_redirect / /superset/;
        proxy_request_buffering off;
        client_max_body_size 50m;
        proxy_connect_timeout 300s;
        proxy_read_timeout 300s;
        proxy_send_timeout 300s;
        sub_filter_once off;
        sub_filter_types text/html;
        sub_filter 'href="/static/' 'href="/superset/static/';
        sub_filter 'src="/static/' 'src="/superset/static/';
        sub_filter 'action="/login/' 'action="/superset/login/';
        sub_filter 'action="/logout/' 'action="/superset/logout/';
        sub_filter 'action="/signup/' 'action="/superset/signup/';
        sub_filter 'action="/reset/' 'action="/superset/reset/';
        sub_filter "if ('serviceWorker' in navigator)" "if (false)";
    }'''

cfg = cfg.replace(old, new)

with sftp.open('/etc/nginx/sites-enabled/vectornode.ru', 'w') as f:
    f.write(cfg.encode())
sftp.close()

stdin, stdout, stderr = ssh.exec_command('nginx -t 2>&1 && systemctl reload nginx 2>&1')
print(stdout.read().decode(errors='replace').strip())

# Also update Superset config to handle prefix
stdin2, stdout2, stderr2 = ssh.exec_command(
    "docker exec podft-superset sh -c \"grep -q 'x_prefix' /app/pythonpath/superset_config.py && echo 'already set' || echo 'need update'\""
)
result = stdout2.read().decode(errors='replace').strip()
print('Config check:', result)

if 'need' in result:
    stdin3, stdout3, stderr3 = ssh.exec_command(
        "docker exec podft-superset sh -c \"sed -i 's/PROXY_FIX_CONFIG = {\\\"x_for\\\": 1, \\\"x_proto\\\": 1, \\\"x_host\\\": 1, \\\"x_port\\\": 1}/PROXY_FIX_CONFIG = {\\\"x_for\\\": 1, \\\"x_proto\\\": 1, \\\"x_host\\\": 1, \\\"x_port\\\": 1, \\\"x_prefix\\\": 1}/' /app/pythonpath/superset_config.py && echo 'updated'\""
    )
    print(stdout3.read().decode(errors='replace').strip())

# Reload Superset container
stdin4, stdout4, stderr4 = ssh.exec_command('docker restart podft-superset 2>&1')
print('Superset restart:', stdout4.read().decode(errors='replace').strip())

# Wait and test
import time
time.sleep(5)

# Test login with web form
stdin5, stdout5, stderr5 = ssh.exec_command(
    "curl -s -D - -o /dev/null -X POST https://vectornode.ru/superset/login/ "
    "-d 'username=admin&password=admin' "
    "-H 'Content-Type: application/x-www-form-urlencoded' "
    "-H 'Referer: https://vectornode.ru/superset/login/' 2>&1 | head -10"
)
print('\nWeb login test:')
print(stdout5.read().decode(errors='replace').strip())

ssh.close()
