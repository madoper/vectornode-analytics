import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

sftp = ssh.open_sftp()
with sftp.open('/etc/nginx/sites-enabled/vectornode.ru', 'r') as f:
    cfg = f.read().decode('utf-8', errors='replace')

# Add sub_filter rules for SPA bootstrap JSON data and action URLs
old = '''        sub_filter 'action="/login/' 'action="/superset/login/';
        sub_filter 'action="/logout/' 'action="/superset/logout/';
        sub_filter 'action="/signup/' 'action="/superset/signup/';
        sub_filter 'action="/reset/' 'action="/superset/reset/';
        sub_filter "if ('serviceWorker' in navigator)" "if (false)";'''

new = '''        sub_filter 'action="/login/' 'action="/superset/login/';
        sub_filter 'action="/logout/' 'action="/superset/logout/';
        sub_filter 'action="/signup/' 'action="/superset/signup/';
        sub_filter 'action="/reset/' 'action="/superset/reset/';
        sub_filter '"user_login_url":"/login/"' '"user_login_url":"/superset/login/"';
        sub_filter '"user_logout_url":"/logout/"' '"user_logout_url":"/superset/logout/"';
        sub_filter '"user_info_url":"/user_info/"' '"user_info_url":"/superset/user_info/"';
        sub_filter '"brandLogoHref":"/"' '"brandLogoHref":"/superset/"';
        sub_filter '"path":"/superset/welcome/"' '"path":"/superset/welcome/"';
        sub_filter "if ('serviceWorker' in navigator)" "if (false)";'''

cfg = cfg.replace(old, new)

# Also add location for /login/ that proxies to Superset as fallback
old2 = '''    # No-op service worker to prevent 404 errors
    location = /static/service-worker.js {'''

new2 = '''    # Catch Superset SPA navigation URLs that lack /superset/ prefix
    location /login/ {
        proxy_pass http://127.0.0.1:8088/login/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Prefix /superset;
    }

    location /logout/ {
        proxy_pass http://127.0.0.1:8088/logout/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Prefix /superset;
    }

    # No-op service worker to prevent 404 errors
    location = /static/service-worker.js {'''

cfg = cfg.replace(old2, new2)

with sftp.open('/etc/nginx/sites-enabled/vectornode.ru', 'w') as f:
    f.write(cfg.encode())
sftp.close()

stdin, stdout, stderr = ssh.exec_command('nginx -t 2>&1 && systemctl reload nginx 2>&1')
print(stdout.read().decode(errors='replace').strip())

# Test
import time
time.sleep(2)

# Verify login page works
stdin2, stdout2, stderr2 = ssh.exec_command(
    "curl -s -o /dev/null -w '%{http_code}' https://vectornode.ru/superset/login/"
)
print('Superset login:', stdout2.read().decode(errors='replace').strip())

# Test /login/ fallback
stdin3, stdout3, stderr3 = ssh.exec_command(
    "curl -s -o /dev/null -w '%{http_code}' https://vectornode.ru/login/"
)
print('/login/ endpoint:', stdout3.read().decode(errors='replace').strip())

ssh.close()
