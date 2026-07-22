import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

sftp = ssh.open_sftp()
with sftp.open('/etc/nginx/sites-enabled/vectornode.ru', 'r') as f:
    cfg = f.read().decode('utf-8', errors='replace')

old_js = """sub_filter '<head>' '<head><script>var _p=JSON.parse;JSON.parse=function(s){var d=_p.apply(this,arguments);if(d&&d.common&&d.common.application_root==="/"){d.common.application_root="/superset";d.common.user_info_url="/superset/user_info/";if(d.common.menu_data&&d.common.menu_data.navbar_right){d.common.menu_data.navbar_right.user_login_url="/superset/login/";d.common.menu_data.navbar_right.user_logout_url="/superset/logout/"}}return d;};</script>';"""

new_js = """sub_filter '<head>' '<head><script>var _p=JSON.parse;JSON.parse=function(s){var d=_p.apply(this,arguments);if(d&&d.common&&d.common.application_root==="/"){d.common.application_root="/superset";if(d.common.menu_data&&d.common.menu_data.brand&&d.common.menu_data.brand.path&&d.common.menu_data.brand.path.indexOf("/superset/")===0)d.common.menu_data.brand.path=d.common.menu_data.brand.path.slice(9)}return d;};</script>';"""

cfg = cfg.replace(old_js, new_js)

with sftp.open('/etc/nginx/sites-enabled/vectornode.ru', 'w') as f:
    f.write(cfg.encode())

stdin, stdout, stderr = ssh.exec_command('nginx -t 2>&1 && systemctl reload nginx 2>&1')
print('Nginx:', stdout.read().decode(errors='replace').strip())

# Verify
stdin2, stdout2, stderr2 = ssh.exec_command(
    "curl -s https://vectornode.ru/superset/login/ 2>&1 | grep -c 'indexOf.*superset'"
)
print(f'Wrapped: {stdout2.read().decode(errors="replace").strip()}')

ssh.close()
