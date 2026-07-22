import paramiko

HOST = '62.217.183.95'
USER = 'root'
PASS = '8884&JKL%f75'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username=USER, password=PASS, timeout=15)

script = r'''
set -e
export AIRFLOW_HOME=/opt/analytics
export PATH=/opt/analytics/venv/bin:$PATH

cd /opt/analytics

# Generate default config then modify it
airflow config list --defaults > /dev/null 2>&1 || true

# Remove any old airflow.cfg and generate fresh one
rm -f airflow.cfg
airflow version 2>/dev/null

# Generate airflow.cfg
python -c "
from airflow.configuration import conf
conf.load_test_config()

# Write the config to file
import configparser
parser = configparser.ConfigParser()

# Read defaults from Airflow
from airflow.configuration import parameterized_config
default_text = parameterized_config(conf.as_dict(display_source=False, include_env=False, include_connections=False))
import tempfile, os

# Write default config
with open(os.path.expanduser('~/airflow.cfg.tmp'), 'w') as f:
    f.write(default_text)
"
'''

stdin, stdout, stderr = ssh.exec_command('echo test')
print(stdout.read().decode().strip())
ssh.close()
