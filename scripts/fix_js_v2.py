import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

sftp = ssh.open_sftp()
with sftp.open('/etc/nginx/sites-enabled/vectornode.ru', 'r') as f:
    cfg = f.read().decode('utf-8', errors='replace')

# Find the problematic line and replace it with clean version
old = '''        sub_filter '</body>' '<script>
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
</script></body>';'''

new = '''        sub_filter '</body>' '<script>!function(){var e=document.getElementById("app");if(e)try{var t=JSON.parse(e.getAttribute("data-bootstrap"));t.common&&(t.common.application_root="/superset",t.common.user_info_url="/superset/user_info/"),e.setAttribute("data-bootstrap",JSON.stringify(t))}catch(e){}}();</script></body>';'''

cfg = cfg.replace(old, new)

with sftp.open('/etc/nginx/sites-enabled/vectornode.ru', 'w') as f:
    f.write(cfg.encode())
sftp.close()

stdin, stdout, stderr = ssh.exec_command('nginx -t 2>&1')
print('Test:', stdout.read().decode(errors='replace').strip())
err = stderr.read().decode(errors='replace').strip()
if err:
    print('ERR:', err[:200])

if 'successful' in (stdout.read().decode(errors='replace') + ''):
    ssh.exec_command('systemctl reload nginx 2>&1')

# Test the injection
stdin2, stdout2, stderr2 = ssh.exec_command(
    "curl -s https://vectornode.ru/superset/login/ 2>&1 | grep -o 'fixBootstrap\\|application_root.*superset\\|user_info.*superset' | head -5"
)
print('\nInjection check:')
print(stdout2.read().decode(errors='replace').strip())

ssh.close()
