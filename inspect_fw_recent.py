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

with sftp.open('C:/apps/bot-keo-nhom-bcr-main/logs/forward_bot_out.log', 'r') as f:
    lines = f.read().decode('utf-8', errors='replace').splitlines()
    for l in lines[-60:]:
        print(l)

sftp.close()
ssh.close()
