import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=10)

# Read current config
_, o, _ = ssh.exec_command('cat /opt/podft/infra/superset-init/superset_config.py')
config = o.read().decode(errors='replace')
print('Current config length:', len(config))

# Check if FEATURE_FLAGS already exists
if 'FEATURE_FLAGS' in config:
    print('FEATURE_FLAGS already exists, check it')
elif 'DASHBOARD_NATIVE_FILTERS' in config:
    print('DASHBOARD_NATIVE_FILTERS already exists')
else:
    # Add FEATURE_FLAGS before the Proxy Fix config
    new_block = '''
FEATURE_FLAGS = {
    "DASHBOARD_NATIVE_FILTERS": True,
    "DASHBOARD_CROSS_FILTERS": True,
    "DASHBOARD_NATIVE_FILTERS_SET": True,
    "DASHBOARD_FILTERS_EXPERIMENTAL": True,
}

'''
    config = config.replace("ENABLE_PROXY_FIX = True", new_block + "ENABLE_PROXY_FIX = True")
    
    # Write back
    sftp = ssh.open_sftp()
    f = sftp.file('/opt/podft/infra/superset-init/superset_config.py', 'w')
    f.write(config)
    f.close()
    sftp.close()
    print('FEATURE_FLAGS added')

    # Restart superset
    _, o2, _ = ssh.exec_command('docker restart podft-superset 2>&1')
    print('Restart:', o2.read().decode(errors='replace'))
    
    # Wait a few seconds and check
    import time
    time.sleep(5)
    _, o3, _ = ssh.exec_command('docker logs podft-superset --tail 5 2>&1')
    print('Logs:', o3.read().decode(errors='replace')[-300:])

ssh.close()
