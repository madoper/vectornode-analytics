import paramiko, socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.settimeout(5)
try:
    result = sock.connect_ex(('62.217.183.95', 22))
    print('Port 22: ' + ('open' if result == 0 else 'closed') + ' (code=' + str(result) + ')')
except Exception as e:
    print('Error: ' + str(e))
finally:
    sock.close()
