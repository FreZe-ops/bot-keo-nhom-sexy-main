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

cmd = r'cd /d C:\apps\bot-keo-nhom-bcr-main & C:\tools\python\python.exe sign_in_bot2_vps.py 72539 gg88vip86'
stdin, stdout, stderr = ssh.exec_command(cmd)

print("=== SIGN IN OUTPUT ===")
print(stdout.read().decode('utf-8', errors='replace'))
print("=== ERROR OUTPUT ===")
print(stderr.read().decode('utf-8', errors='replace'))

ssh.close()
