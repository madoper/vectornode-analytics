import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

sftp = ssh.open_sftp()
with sftp.open('/etc/nginx/sites-enabled/vectornode.ru', 'r') as f:
    cfg = f.read().decode('utf-8', errors='replace')

# Replace DOMContentLoaded injection with JSON.parse wrapper
old_js = """sub_filter '<head>' '<head><script>function _fixSS(){var e=document.getElementById("app");if(e)try{var t=JSON.parse(e.getAttribute("data-bootstrap"));if(t.common){t.common.application_root="/superset";t.common.user_info_url="/superset/user_info/";if(t.common.menu_data&&t.common.menu_data.navbar_right){t.common.menu_data.navbar_right.user_login_url="/superset/login/";t.common.menu_data.navbar_right.user_logout_url="/superset/logout/"}e.setAttribute("data-bootstrap",JSON.stringify(t))}}catch(e){}}document.addEventListener("DOMContentLoaded",_fixSS);</script>';"""

new_js = """sub_filter '<head>' '<head><script>var _p=JSON.parse;JSON.parse=function(s){var d=_p.apply(this,arguments);if(d&&d.common&&d.common.application_root==="/"){d.common.application_root="/superset";d.common.user_info_url="/superset/user_info/";if(d.common.menu_data&&d.common.menu_data.navbar_right){d.common.menu_data.navbar_right.user_login_url="/superset/login/";d.common.menu_data.navbar_right.user_logout_url="/superset/logout/"}}return d;};</script>';"""

cfg = cfg.replace(old_js, new_js)

with sftp.open('/etc/nginx/sites-enabled/vectornode.ru', 'w') as f:
    f.write(cfg.encode())

stdin, stdout, stderr = ssh.exec_command('nginx -t 2>&1')
result = stdout.read().decode(errors='replace').strip()
print('Test:', result)

if 'successful' in result:
    ssh.exec_command('systemctl reload nginx 2>&1')
    print('Reloaded')

# Verify injection present
stdin2, stdout2, stderr2 = ssh.exec_command(
    "curl -s https://vectornode.ru/superset/login/ 2>&1 | grep -c '_p.apply'"
)
print(f'Injection found: {stdout2.read().decode(errors="replace").strip()} times')

# Simulate SPA bootstrap read
stdin3, stdout3, stderr3 = ssh.exec_command(
    "curl -s https://vectornode.ru/superset/login/ 2>&1 | grep -oE 'application_root\":\"[^\"]*\"'"
)
print(f'application_root in HTML: {stdout3.read().decode(errors="replace").strip()}')

ssh.close()
