import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

sftp = ssh.open_sftp()
with sftp.open('/etc/nginx/sites-enabled/vectornode.ru', 'r') as f:
    cfg = f.read().decode('utf-8', errors='replace')

# Add variable definition and sub_filter rules for HTML-encoded JSON
old = '''        sub_filter '"user_login_url":"/login/"' '"user_login_url":"/superset/login/"';
        sub_filter '"user_logout_url":"/logout/"' '"user_logout_url":"/superset/logout/"';
        sub_filter '"user_info_url":"/user_info/"' '"user_info_url":"/superset/user_info/"';
        sub_filter '"brandLogoHref":"/"' '"brandLogoHref":"/superset/"';
        sub_filter '"path":"/superset/welcome/"' '"path":"/superset/welcome/"';
        sub_filter "if ('serviceWorker' in navigator)" "if (false)";'''

new = '''        set $dq "&#34;";
        sub_filter '$dq/user_info/$dq' '$dq/superset/user_info/$dq';
        sub_filter '$dqapplication_root$dq: $dq/$dq' '$dqapplication_root$dq: $dq/superset/$dq';
        sub_filter "if ('serviceWorker' in navigator)" "if (false)";'''

cfg = cfg.replace(old, new)

with sftp.open('/etc/nginx/sites-enabled/vectornode.ru', 'w') as f:
    f.write(cfg.encode())
sftp.close()

# Test config
stdin, stdout, stderr = ssh.exec_command('nginx -t 2>&1')
print('Config test:', stdout.read().decode(errors='replace').strip())

# Reload
stdin2, stdout2, stderr2 = ssh.exec_command('systemctl reload nginx 2>&1')
print('Reload:', stdout2.read().decode(errors='replace').strip())

# Test
stdin3, stdout3, stderr3 = ssh.exec_command(
    "curl -s https://vectornode.ru/superset/login/ 2>&1 | grep -oP 'user_info_url[^,}]*|application_root[^,}]*'"
)
print('\nAfter fix:')
print(stdout3.read().decode(errors='replace').strip())

ssh.close()
