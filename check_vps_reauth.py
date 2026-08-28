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

# Đọc log mới nhất sau khi restart
sftp = ssh.open_sftp()
path = 'C:/apps/bot-keo-nhom-bcr-main/logs/forward_bot_out.log'
try:
    with sftp.open(path, 'r') as f:
        f.seek(0, 2)
        size = f.tell()
        f.seek(max(0, size - 2000), 0)
        print("=== NEW LOG AFTER RESTART ===")
        print(f.read().decode('utf-8', errors='replace'))
except Exception as e:
    print(f"Error reading log: {e}")

sftp.close()
ssh.close()
