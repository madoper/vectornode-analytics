import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

sftp = ssh.open_sftp()
with sftp.open('/etc/nginx/sites-enabled/vectornode.ru', 'r') as f:
    cfg = f.read().decode('utf-8', errors='replace')

# Remove broken sub_filter rules, add JS injection
old = '''        sub_filter '"user_info_url":"' '"user_info_url":"/superset';
        sub_filter '"application_root":"' '"application_root":"/superset';'''

fix_js = '''<script>
(function fixBootstrap() {
  var el = document.getElementById('app');
  if (!el) return;
  try {
    var d = JSON.parse(el.getAttribute('data-bootstrap'));
    if (d.common) {
      d.common.application_root = '/superset';
      d.common.user_info_url = '/superset/user_info/';
    }
    el.setAttribute('data-bootstrap', JSON.stringify(d));
  } catch(e) {}
})();
</script></body>'''

new = f'''        sub_filter '</body>' '{fix_js}';'''

cfg = cfg.replace(old, new)

with sftp.open('/etc/nginx/sites-enabled/vectornode.ru', 'w') as f:
    f.write(cfg.encode())
sftp.close()

stdin, stdout, stderr = ssh.exec_command('nginx -t 2>&1 && systemctl reload nginx 2>&1')
print('Nginx:', stdout.read().decode(errors='replace').strip())

# Test
stdin2, stdout2, stderr2 = ssh.exec_command(
    "curl -s https://vectornode.ru/superset/login/ 2>&1 | grep -oP 'application_root[^,}]*|user_info_url[^,}]*|fixBootstrap'"
)
print('Bootstrap:', stdout2.read().decode(errors='replace').strip())

ssh.close()
