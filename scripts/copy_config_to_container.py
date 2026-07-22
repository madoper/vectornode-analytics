import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=15)

# Create a fixed superset_config.py on the host
config_content = '''import os

SECRET_KEY = os.getenv("SUPERSET_SECRET_KEY", "change-me")

_db_host = os.getenv("POSTGRES_HOST", "postgres")
_db_port = os.getenv("POSTGRES_PORT", "5432")
_db_user = os.getenv("POSTGRES_USER", "podft")
_db_pass = os.getenv("POSTGRES_PASSWORD", "podft-secret")
_db_name = os.getenv("POSTGRES_DB", "superset")

SQLALCHEMY_DATABASE_URI = (
    f"postgresql+psycopg2://{_db_user}:{_db_pass}@"
    f"{_db_host}:{_db_port}/{_db_name}"
)

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = os.getenv("REDIS_PORT", "6379")
REDIS_CACHE_DB = os.getenv("REDIS_CACHE_DB", "1")

RESULTS_BACKEND = {
    "function": "superset.utils.redis.get_redis_result_backend",
    "key": f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_CACHE_DB}",
}

CACHE_CONFIG = {
    "CACHE_TYPE": "RedisCache",
    "CACHE_DEFAULT_TIMEOUT": 300,
    "CACHE_KEY_PREFIX": "superset_",
    "CACHE_REDIS_URL": f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_CACHE_DB}",
}

DATA_CACHE_CONFIG = CACHE_CONFIG

ENABLE_PROXY_FIX = True

ROW_LIMIT = 5000

SUPERSET_WEBSERVER_PORT = int(os.getenv("SUPERSET_PORT", 8088))

WTF_CSRF_ENABLED = True
WTF_CSRF_EXEMPT_LIST = []
TALISMAN_ENABLED = False

ENABLE_PROXY_FIX = True
PROXY_FIX_CONFIG = {"x_for": 1, "x_proto": 1, "x_host": 1, "x_port": 1, "x_prefix": 1}
'''

# Write it
sftp = ssh.open_sftp()
with sftp.open('/opt/analytics/scripts/superset_config.py', 'w') as f:
    f.write(config_content.encode())
sftp.close()
print('Config written')

# Copy to container using docker cp with a temp file trick
stdin, stdout, stderr = ssh.exec_command(
    'docker cp /opt/analytics/scripts/superset_config.py podft-superset:/tmp/superset_config.py 2>&1 && '
    'docker exec podft-superset sh -c "cp /tmp/superset_config.py /app/pythonpath/superset_config.py" 2>&1'
)
print('Copy result:')
print(stdout.read().decode(errors='replace').strip())
err = stderr.read().decode(errors='replace').strip()
if err:
    print('ERROR:', err[:300])

# Check if it worked
stdin2, stdout2, stderr2 = ssh.exec_command(
    'docker exec podft-superset grep "x_prefix" /app/pythonpath/superset_config.py'
)
print('After copy:', stdout2.read().decode(errors='replace').strip())

ssh.close()
