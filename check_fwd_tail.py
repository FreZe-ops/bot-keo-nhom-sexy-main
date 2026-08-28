import paramiko
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('180.93.235.84', port=22, username='administrator', password='uK?fdJ4Qo!7v', timeout=15)

stdin, stdout, stderr = ssh.exec_command('powershell -Command "Get-Content C:\\apps\\bot-keo-nhom-bcr-main\\logs\\forward_bot_out.log -Tail 20"')
print("=== FORWARD OUT ===")
print(stdout.read().decode('utf-8', errors='replace'))

stdin, stdout, stderr = ssh.exec_command('powershell -Command "Get-Content C:\\apps\\bot-keo-nhom-bcr-main\\logs\\forward_bot_err.log -Tail 20"')
print("=== FORWARD ERR ===")
print(stdout.read().decode('utf-8', errors='replace'))

ssh.close()
