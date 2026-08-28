import paramiko
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('180.93.235.84', port=22, username='administrator', password='uK?fdJ4Qo!7v', timeout=15)

stdin, stdout, stderr = ssh.exec_command('powershell -Command "dir C:\\apps\\bot-keo-nhom-bcr-main\\*.session"')
print(stdout.read().decode('utf-8', errors='replace'))

ssh.close()
