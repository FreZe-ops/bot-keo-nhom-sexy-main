import paramiko
import sys
import time

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
sftp = ssh.open_sftp()

time.sleep(5)

print("=== CHECKING ALL 4 BOTS LOGS ===")
for b in [1, 2, 3, 4]:
    path = f'C:/apps/bot-keo-nhom-bcr-main/logs/bot{b}-out.log'
    print(f"\n==================== BOT {b} LOG ====================")
    try:
        stat = sftp.stat(path)
        with sftp.open(path, 'r') as f:
            f.seek(max(0, stat.st_size - 1500), 0)
            lines = f.read().decode('utf-8', errors='replace').splitlines()[-8:]
            for l in lines:
                print(l)
    except Exception as e:
        print(f"Error: {e}")

sftp.close()
ssh.close()
