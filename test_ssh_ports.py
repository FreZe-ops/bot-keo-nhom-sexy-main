import paramiko
import sys

HOST = '180.93.235.84'
PASS = 'uK?fdJ4Qo!7v'

combos = [
    (55293, 'administrator'),
    (22, 'administrator'),
    (22, 'root'),
    (55293, 'root')
]

for port, user in combos:
    print(f"\n--- Testing SSH to {user}@{HOST}:{port} ---")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(HOST, port=port, username=user, password=PASS, timeout=8)
        print(f"SUCCESS! Connected to {user}@{HOST}:{port}")
        stdin, stdout, stderr = ssh.exec_command('whoami; uptime; uname -a', timeout=10)
        print(stdout.read().decode('utf-8', errors='replace'))
        ssh.close()
        break
    except Exception as e:
        print(f"Failed: {e}")
