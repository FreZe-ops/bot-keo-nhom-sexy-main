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

print("==================== LATEST 80 LINES OF forward_bot_out.log ====================")
path = 'C:/apps/bot-keo-nhom-bcr-main/logs/forward_bot_out.log'
try:
    with sftp.open(path, 'r') as f:
        f.seek(0, 2)
        sz = f.tell()
        f.seek(max(0, sz - 8000), 0)
        lines = f.read().decode('utf-8', errors='replace').splitlines()[-80:]
        for l in lines:
            print(l)
except Exception as e:
    print(f"Error: {e}")

sftp.close()
ssh.close()
