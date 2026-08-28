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
with sftp.open('C:/apps/bot-keo-nhom-bcr-main/.env', 'r') as f:
    content = f.read().decode('utf-8', errors='replace')
print("=== VPS .ENV CONTENT ===")
print(content)
sftp.close()
ssh.close()
