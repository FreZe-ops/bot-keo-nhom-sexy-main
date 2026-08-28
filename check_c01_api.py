import paramiko
import sys

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

HOST = '180.93.235.84'
PORT = 22
USER = 'administrator'
PASS = 'uK?fdJ4Qo!7v'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, port=PORT, username=USER, password=PASS, timeout=15)

cmd = r'''
C:\tools\python\python.exe -c "
import urllib.request, json
req = urllib.request.Request('http://127.0.0.1:3000/api/latest-screenshot?tableName=C01')
res = urllib.request.urlopen(req).read().decode('utf-8')
print(res)
"
'''
stdin, stdout, stderr = ssh.exec_command(cmd)
print("Latest screenshot API C01:")
print(stdout.read().decode('utf-8', errors='replace'))

ssh.close()
