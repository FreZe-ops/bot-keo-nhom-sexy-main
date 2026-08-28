import paramiko
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('180.93.235.84', port=22, username='administrator', password='uK?fdJ4Qo!7v', timeout=15)

stdin, stdout, stderr = ssh.exec_command('powershell -Command "Get-ChildItem -Path C:\\Users\\administrator -Filter *84365618453* | Select-Object FullName, Length, LastWriteTime"')
print(stdout.read().decode('utf-8', errors='replace'))

stdin, stdout, stderr = ssh.exec_command('powershell -Command "Copy-Item C:\\Users\\administrator\\user_session_84365618453.session C:\\apps\\bot-keo-nhom-bcr-main\\user_session_84365618453.session -Force"')
print("Copied to C:\\apps\\bot-keo-nhom-bcr-main")

NSSM = r'C:\tools\nssm\nssm-2.24\win64\nssm.exe'
stdin, stdout, stderr = ssh.exec_command(f'{NSSM} restart BCR-forward-bot')
print('Restart BCR-forward-bot:', stdout.read().decode('utf-8', errors='replace').strip())

ssh.close()
