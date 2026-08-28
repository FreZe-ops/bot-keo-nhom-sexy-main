import paramiko
import sys

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

HOST = '180.93.235.84'
PORT = 22
USER = 'administrator'
PASS = 'uK?fdJ4Qo!7v'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, port=PORT, username=USER, password=PASS, timeout=15)
sftp = ssh.open_sftp()

print("==================== LATEST 20 LINES OF session2-out.log ====================")
path = 'C:/apps/bot-keo-nhom-bcr-main/logs/session2-out.log'
try:
    with sftp.open(path, 'r') as f:
        f.seek(0, 2)
        sz = f.tell()
        f.seek(max(0, sz - 4000), 0)
        lines = f.read().decode('utf-8', errors='replace').splitlines()[-20:]
        for l in lines:
            print(l)
except Exception as e:
    print(f"Error: {e}")

print("\n==================== HEALTH CHECK ALL SESSIONS ====================")
stdin, stdout, stderr = ssh.exec_command(r'cd /d C:\apps\bot-keo-nhom-bcr-main & C:\tools\python\python.exe vps_health_check.py')
print(stdout.read().decode('utf-8', errors='replace'))

sftp.close()
ssh.close()
