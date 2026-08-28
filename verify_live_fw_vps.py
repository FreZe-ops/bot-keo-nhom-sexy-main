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

NSSM = r'C:\tools\nssm\nssm-2.24\win64\nssm.exe'

print("=== RESTARTING BCR-forward-bot SERVICE ===")
stdin, stdout, stderr = ssh.exec_command(f'{NSSM} restart BCR-forward-bot')
print(stdout.read().decode('utf-8', errors='replace'))

print("Waiting 15s for live ca execution synced with Table C01...")
time.sleep(15)

sftp = ssh.open_sftp()
path = 'C:/apps/bot-keo-nhom-bcr-main/logs/forward_bot_out.log'
try:
    with sftp.open(path, 'r') as f:
        f.seek(0, 2)
        size = f.tell()
        f.seek(max(0, size - 3000), 0)
        print("\n=== LIVE FORWARD BOT LOG ON VPS ===")
        print(f.read().decode('utf-8', errors='replace'))
except Exception as e:
    print(f"Error reading log: {e}")

sftp.close()
ssh.close()
