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

script = """
import urllib.request
import json

for path in ['/api/tables', '/api/current-table', '/api/latest-screenshot', '/api/status']:
    url = f'http://localhost:3201{path}'
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=3) as r:
            res = json.loads(r.read().decode('utf-8'))
            print(f'API {path}: SUCCESS ->', str(res)[:120])
    except Exception as e:
        print(f'API {path}: ERROR -> {e}')
"""

stdin, stdout, stderr = ssh.exec_command(f'C:\\tools\\python\\python.exe -c "{script}"')
print(stdout.read().decode('utf-8', errors='replace'))
print(stderr.read().decode('utf-8', errors='replace'))
ssh.close()
