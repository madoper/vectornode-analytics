import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.217.183.95', username='root', password='8884&JKL%f75', timeout=10, look_for_keys=False, allow_agent=False)

stdin, stdout, stderr = ssh.exec_command('tail -5 /tmp/build_bot.log 2>/dev/null')
print('BOT BUILD:', stdout.read().decode())

stdin, stdout, stderr = ssh.exec_command('docker images podft-* --format "{{.Repository}}:{{.Tag}} {{.Size}}"')
print('IMAGES:', stdout.read().decode())

# Start embedding
stdin, stdout, stderr = ssh.exec_command('docker run -d --name podft-embedding --network podft_podft-net -p 5100:5100 -e MODEL_NAME=BAAI/bge-small-ru -e DEVICE=cpu --restart unless-stopped podft-embedding:latest 2>&1')
print('EMBEDDING START:', stdout.read().decode())

# Start telegram bot  
stdin, stdout, stderr = ssh.exec_command('docker run -d --name podft-telegram-bot --network podft_podft-net -e BOT_TOKEN=8902035039:AAFhttq7heF76HUW5aKnCSU2Y7mbL8aijV4 -e GATEWAY_URL=http://gateway:8000 --restart unless-stopped podft-telegram-bot:latest 2>&1')
print('BOT START:', stdout.read().decode())

ssh.close()
