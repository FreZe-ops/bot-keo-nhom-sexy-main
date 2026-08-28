import paramiko, sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('180.93.235.84', 22, 'administrator', 'uK?fdJ4Qo!7v', timeout=20)
remote = r'''
import re
p = r"C:\apps\bot-keo-nhom-bcr-main\logs\session1-out.log"
with open(p,"r",encoding="utf-8",errors="ignore") as f:
    lines = f.readlines()[-6000:]
pat = re.compile(r"BROWSER|popup|Xác nhận|mouse_|CLICK TABLE|attempt|reserved|probe", re.I)
for l in lines:
    if pat.search(l):
        print(l.rstrip().encode("ascii","backslashreplace").decode())
'[-40:]
'''
sftp = ssh.open_sftp()
with sftp.open('C:/apps/bot-keo-nhom-bcr-main/t5.py','w') as f: f.write(remote)
sftp.close()
stdin,stdout,stderr=ssh.exec_command(r'C:\tools\python\python.exe C:\apps\bot-keo-nhom-bcr-main\t5.py')
print(stdout.read().decode())
ssh.close()
