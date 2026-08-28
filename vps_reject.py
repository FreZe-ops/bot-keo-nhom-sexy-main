import paramiko, sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('180.93.235.84', 22, 'administrator', 'uK?fdJ4Qo!7v', timeout=20)
remote = r'''
import re
p = r"C:\apps\bot-keo-nhom-bcr-main\logs\session1-out.log"
pat = re.compile(r"LOBBY|REJECT|FAIL|FATAL|blank|signal|SAVED|chụp thành công|SCREENSHOT FAIL", re.I)
with open(p, "r", encoding="utf-8", errors="ignore") as f:
    lines = f.readlines()
hits = [l.rstrip() for l in lines[-12000:] if pat.search(l)]
for l in hits[-40:]:
    print(l.encode("ascii", "backslashreplace").decode())
'''
sftp = ssh.open_sftp()
with sftp.open('C:/apps/bot-keo-nhom-bcr-main/t2.py', 'w') as f:
    f.write(remote.encode('utf-8'))
sftp.close()
stdin, stdout, stderr = ssh.exec_command(r'C:\tools\python\python.exe C:\apps\bot-keo-nhom-bcr-main\t2.py')
print(stdout.read().decode('utf-8', errors='replace'))
ssh.close()
