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
sftp = ssh.open_sftp()

def check_log(filename):
    print(f"\n==================== LOG: {filename} ====================")
    try:
        path = f'C:/apps/bot-keo-nhom-bcr-main/logs/{filename}'
        with sftp.open(path, 'r') as f:
            f.seek(0, 2)
            size = f.tell()
            f.seek(max(0, size - 2000), 0)
            print(f.read().decode('utf-8', errors='replace'))
    except Exception as e:
        print(f"Error reading {filename}: {e}")

check_log('forward_bot_out.log')
check_log('forward_bot_err.log')

sftp.close()
ssh.close()
