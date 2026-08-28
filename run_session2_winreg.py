import paramiko
import sys
import time

HOST = '180.93.235.84'
PORT = 22
USER = 'administrator'
PASS = 'uK?fdJ4Qo!7v'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, port=PORT, username=USER, password=PASS, timeout=15)
sftp = ssh.open_sftp()

sftp.put('d:/BOT KEO NHOM BCR/bot-keo-nhom-bcr-main/set_session2_winreg.py', 'C:/apps/bot-keo-nhom-bcr-main/set_session2_winreg.py')
sftp.close()

stdin, stdout, stderr = ssh.exec_command(r'C:\tools\python\python.exe C:\apps\bot-keo-nhom-bcr-main\set_session2_winreg.py')
print(stdout.read().decode('utf-8', errors='replace'))

NSSM = r'C:\tools\nssm\nssm-2.24\win64\nssm.exe'

# Xóa các file lock cũ
ssh.exec_command(r'del /f /q C:\Users\Administrator\AppData\Local\Temp\sexy-account-*.lock 2>nul')

stdin, stdout, stderr = ssh.exec_command(f'{NSSM} restart BCR-session2 & {NSSM} restart BCR-bot2')
print(stdout.read().decode('utf-8', errors='replace'))

time.sleep(3)

stdin, stdout, stderr = ssh.exec_command(f'{NSSM} get BCR-session2 AppEnvironmentExtra')
print("VERIFY NSSM GET:")
print(stdout.read().decode('utf-8', errors='replace'))

ssh.close()
