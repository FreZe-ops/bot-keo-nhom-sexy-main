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

CODE = sys.argv[1] if len(sys.argv) > 1 else '95762'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, port=PORT, username=USER, password=PASS, timeout=15)

stdin, stdout, stderr = ssh.exec_command(f'cd /d C:\\apps\\bot-keo-nhom-bcr-main & C:\\tools\\python\\python.exe submit_with_hash.py {CODE}')
out = stdout.read().decode('utf-8', errors='replace')
err = stderr.read().decode('utf-8', errors='replace')
print("=== VPS SIGN-IN RESULT ===")
print(out)
if err.strip():
    print(f"[STDERR]: {err}")

ssh.close()
