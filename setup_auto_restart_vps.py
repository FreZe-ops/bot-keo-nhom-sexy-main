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

print("1. Uploading auto_restart_sessions.py...")
sftp.put('d:/BOT KEO NHOM BCR/bot-keo-nhom-bcr-main/auto_restart_sessions.py', 'C:/apps/bot-keo-nhom-bcr-main/auto_restart_sessions.py')
sftp.close()

print("2. Creating Windows Scheduled Task for 2-hour auto restart...")
cmd_create = r'schtasks /create /tn "BCR_AutoRestart_2Hours" /tr "C:\tools\python\python.exe C:\apps\bot-keo-nhom-bcr-main\auto_restart_sessions.py" /sc HOURLY /mo 2 /ru "SYSTEM" /f'
stdin, stdout, stderr = ssh.exec_command(cmd_create)
print(stdout.read().decode('utf-8', errors='replace'))
print(stderr.read().decode('utf-8', errors='replace'))

print("3. Verifying Scheduled Task details...")
stdin, stdout, stderr = ssh.exec_command('schtasks /query /tn "BCR_AutoRestart_2Hours" /v /fo LIST')
print(stdout.read().decode('utf-8', errors='replace'))

ssh.close()
print("Setup auto-restart every 2 hours completed successfully!")
