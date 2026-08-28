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

print("1. Uploading tele_forward_accounts.json...")
sftp.put('d:/BOT KEO NHOM BCR/bot-keo-nhom-bcr-main/tele_forward_accounts.json', 'C:/apps/bot-keo-nhom-bcr-main/tele_forward_accounts.json')

print("2. Uploading bot_forward_runner.py...")
sftp.put('d:/BOT KEO NHOM BCR/bot-keo-nhom-bcr-main/bot_forward_runner.py', 'C:/apps/bot-keo-nhom-bcr-main/bot_forward_runner.py')

sftp.close()
ssh.close()
print("Files uploaded successfully to VPS!")
