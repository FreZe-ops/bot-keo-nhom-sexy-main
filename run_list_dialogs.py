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

sftp.put('d:/BOT KEO NHOM BCR/bot-keo-nhom-bcr-main/list_dialogs_vps.py', 'C:/apps/bot-keo-nhom-bcr-main/list_dialogs_vps.py')
sftp.close()

cmd = r'cd /d C:\apps\bot-keo-nhom-bcr-main & C:\tools\python\python.exe list_dialogs_vps.py'
stdin, stdout, stderr = ssh.exec_command(cmd)

print("=== DIALOGS OUTPUT ===")
print(stdout.read().decode('utf-8', errors='replace'))

ssh.close()
