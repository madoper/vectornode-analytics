import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=10)

# Check Superset version and native filter feature flag
_, o, _ = ssh.exec_command("docker exec podft-superset superset version 2>/dev/null || echo NOK")
print('Version:', o.read().decode(errors='replace'))

# Check for feature flags related to native filters
_, o2, _ = ssh.exec_command(
    "grep -i 'NATIVE_FILTER\|DASHBOARD_NATIVE_FILTER\|ENABLE_FILTER' "
    "/opt/podft/infra/superset-init/superset_config.py 2>/dev/null || echo 'Not found in config'"
)
print('\nFeature flags:', o2.read().decode(errors='replace'))

# Check if VERSIONED_EXPORT or similar features exist
_, o3, _ = ssh.exec_command(
    "grep -i 'FEATURE_FLAGS\|VERSIONED\|FILTER_BAR\|DASHBOARD_CROSS' "
    "/opt/podft/infra/superset-init/superset_config.py 2>/dev/null || echo 'Not found'"
)
print('\nAll feature-related config:')
print(o3.read().decode(errors='replace'))

ssh.close()
