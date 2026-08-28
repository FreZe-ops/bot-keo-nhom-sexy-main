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

for f in ['forward_bot_out.log', 'forward_bot_err.log']:
    path = f'C:/apps/bot-keo-nhom-bcr-main/logs/{f}'
    print(f"\n==================== {f} ====================")
    try:
        stat = sftp.stat(path)
        with sftp.open(path, 'r') as logf:
            logf.seek(max(0, stat.st_size - 3000), 0)
            print(logf.read().decode('utf-8', errors='replace'))
    except Exception as e:
        print(f"Error reading {f}: {e}")

sftp.close()
ssh.close()
