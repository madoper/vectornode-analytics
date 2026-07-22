import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=10)

# Test unencoded form_data directly on server
_, o, _ = ssh.exec_command(
    'curl -s -k -w "HTTP_%{http_code} LOC=%{redirect_url}" '
    '-X GET "https://bi.vectornode.ru/api/v1/chart/data?form_data=%7B%22slice_id%22%3A5%7D" '
    '-H "Authorization: Bearer test"'
)
print('Test encoded:', o.read().decode(errors='replace')[:200])

# Test unencoded
_, o2, _ = ssh.exec_command(
    'curl -s -k -w "HTTP_%{http_code} LOC=%{redirect_url}" '
    '-X GET "https://bi.vectornode.ru/api/v1/chart/data?form_data=%7B%22slice_id%22:%205%7D" '
    '-H "Authorization: Bearer test"'
)
print('\nTest encoded2:', o2.read().decode(errors='replace')[:200])

# Test using API directly on localhost
_, o3, _ = ssh.exec_command(
    'curl -s -w "HTTP_%{http_code} %{redirect_url}" '
    '"http://localhost/api/v1/chart/data?form_data=%7B%22slice_id%22%3A5%7D" '
    '-H "Host: bi.vectornode.ru"'
)
print('\nTest via localhost:', o3.read().decode(errors='replace')[:200])

ssh.close()
