import paramiko
import sys
import os

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
sftp.put('d:/BOT KEO NHOM BCR/bot-keo-nhom-bcr-main/sign_in_runner.py', 'C:/apps/bot-keo-nhom-bcr-main/sign_in_runner.py')
sftp.close()

stdin, stdout, stderr = ssh.exec_command(r'cd /d C:\apps\bot-keo-nhom-bcr-main & C:\tools\python\python.exe sign_in_runner.py 94937')
print(stdout.read().decode('utf-8', errors='replace'))
print(stderr.read().decode('utf-8', errors='replace'))
ssh.close()
