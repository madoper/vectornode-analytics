import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

sftp = ssh.open_sftp()
with sftp.open('/etc/nginx/sites-enabled/vectornode.ru', 'r') as f:
    cfg = f.read().decode('utf-8', errors='replace')

# Replace DOMContentLoaded with JSON.parse wrapper
old_sub = r"""        sub_filter '<head>' '<head><script>document.addEventListener("DOMContentLoaded",function(){var e=document.getElementById("app");if(e)try{var t=JSON.parse(e.getAttribute("data-bootstrap"));t.common&&(t.common.application_root="/superset",t.common.user_info_url="/superset/user_info/",t.common.menu_data.navbar_right.user_login_url="/superset/login/",t.common.menu_data.navbar_right.user_logout_url="/superset/logout/"),e.setAttribute("data-bootstrap",JSON.stringify(t))}catch(e){}});</script>';"""

new_sub = r"""        sub_filter '<head>' '<head><script>var _origParse=JSON.parse;JSON.parse=function(s){var d=_origParse.apply(this,arguments);if(d&&d.common&&d.common.application_root==="/"){d.common.application_root="/superset";d.common.user_info_url="/superset/user_info/";if(d.common.menu_data&&d.common.menu_data.navbar_right){d.common.menu_data.navbar_right.user_login_url="/superset/login/";d.common.menu_data.navbar_right.user_logout_url="/superset/logout/"}}return d;};</script>';"""

cfg = cfg.replace(old_sub, new_sub)

with sftp.open('/etc/nginx/sites-enabled/vectornode.ru', 'w') as f:
    f.write(cfg.encode())
sftp.close()

stdin, stdout, stderr = ssh.exec_command('nginx -t 2>&1 && systemctl reload nginx 2>&1')
print('Nginx:', stdout.read().decode(errors='replace').strip())

# Verify injection
stdin2, stdout2, stderr2 = ssh.exec_command(
    "curl -s https://vectornode.ru/superset/login/ 2>&1 | grep -c '_origParse'"
)
print(f'Injection found: {stdout2.read().decode(errors="replace").strip()} times')

# Check proxy_redirect in /login/ location
stdin3, stdout3, stderr3 = ssh.exec_command(
    "grep -A 12 'location /login/' /etc/nginx/sites-enabled/vectornode.ru"
)
print('\n/login/ location:')
print(stdout3.read().decode(errors='replace').strip())

ssh.close()
