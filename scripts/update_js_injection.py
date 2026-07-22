import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

sftp = ssh.open_sftp()
with sftp.open('/etc/nginx/sites-enabled/vectornode.ru', 'r') as f:
    cfg = f.read().decode('utf-8', errors='replace')

# Update the JS injection to fix all URLs
old_sub = '''        sub_filter '</body>' '<script>!function(){var e=document.getElementById("app");if(e)try{var t=JSON.parse(e.getAttribute("data-bootstrap"));t.common&&(t.common.application_root="/superset",t.common.user_info_url="/superset/user_info/"),e.setAttribute("data-bootstrap",JSON.stringify(t))}catch(e){}}();</script></body>';'''

new_sub = r"""        sub_filter '</body>' '<script>!function(){var e=document.getElementById("app");if(e)try{var t=JSON.parse(e.getAttribute("data-bootstrap"));t.common&&(t.common.application_root="/superset",t.common.user_info_url="/superset/user_info/",t.common.menu_data.navbar_right.user_login_url="/superset/login/",t.common.menu_data.navbar_right.user_logout_url="/superset/logout/"),e.setAttribute("data-bootstrap",JSON.stringify(t))}catch(e){}}();</script></body>';"""

cfg = cfg.replace(old_sub, new_sub)

with sftp.open('/etc/nginx/sites-enabled/vectornode.ru', 'w') as f:
    f.write(cfg.encode())
sftp.close()

stdin, stdout, stderr = ssh.exec_command('nginx -t 2>&1 && systemctl reload nginx 2>&1')
print('Nginx:', stdout.read().decode(errors='replace').strip())

# Test
stdin2, stdout2, stderr2 = ssh.exec_command(
    "curl -s https://vectornode.ru/superset/login/ 2>&1 | grep -oP 'user_login_url[^,}]*|user_logout_url[^,}]*|user_info_url[^,}]*|application_root[^,}]*|brand.*?path[^,}]*' | head -10"
)
print('\nBootstrap URLs:')
print(stdout2.read().decode(errors='replace').strip())

ssh.close()
