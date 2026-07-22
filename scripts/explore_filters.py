import paramiko, json
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', port=22, username='root', password='8884&JKL%f75', timeout=10)

# 1. Check KeyValueEntry model
cmd = "docker exec podft-superset python3 -c \"from superset.key_value.models import KeyValueEntry; print(KeyValueEntry.__table__.columns.keys())\""
_, o, _ = ssh.exec_command(cmd)
print('KeyValueEntry columns:', o.read().decode(errors='replace'))

# 2. Check filter_state entries in DB
cmd2 = "docker exec podft-postgres psql -U podft -d superset -c \"SELECT id, resource, uuid, LEFT(value::text, 300) as val FROM key_value_entry WHERE resource LIKE '%%filter%%' OR resource LIKE '%%dashboard%%' ORDER BY id DESC LIMIT 10\""
_, o2, _ = ssh.exec_command(cmd2)
print('\nFilter state DB entries:')
print(o2.read().decode(errors='replace'))

# 3. Check the TemporaryCachePostSchema to understand the filter_value format
cmd3 = "docker exec podft-superset cat /app/superset/temporary_cache/schemas.py 2>/dev/null | head -40"
_, o3, _ = ssh.exec_command(cmd3)
print('\nTemporaryCachePostSchema:')
print(o3.read().decode(errors='replace'))

# 4. Check the data method in charts api - how filters are applied
cmd4 = "docker exec podft-superset grep -n 'extra_filters\|applied_filters\|filter_state\|get_filters' /app/superset/charts/data/api.py 2>/dev/null | head -15"
_, o4, _ = ssh.exec_command(cmd4)
print('\nFilter handling in chart API:')
print(o4.read().decode(errors='replace'))

ssh.close()
