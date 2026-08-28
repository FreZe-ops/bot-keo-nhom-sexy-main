import paramiko, sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('180.93.235.84', 22, 'administrator', 'uK?fdJ4Qo!7v', timeout=20)

remote = r'''
import os, re
from urllib.request import urlopen

def safe(s):
    return s.encode("ascii", "backslashreplace").decode("ascii")

try:
    with urlopen("http://127.0.0.1:3201/api/session-progress", timeout=5) as r:
        print("SESSION_PROGRESS", safe(r.read().decode()))
except Exception as e:
    print("ERR", e)

base = r"C:\apps\bot-keo-nhom-bcr-main"
pat = re.compile(r"SCREENSHOT|FATAL|IN ROOM|ENTER|probe|CHUA|CHƯA|resetMain|WATCHDOG|CLICK TABLE|API NOTIFY|consecutive", re.I)
for i in range(1, 5):
    p = os.path.join(base, f"logs/session{i}-out.log")
    with open(p, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()
    print("\n=== NS%d last 15 hits (of %d lines) ===" % (i, len(lines)))
    hits = [l.rstrip() for l in lines if pat.search(l)]
    for l in hits[-15:]:
        print(safe(l))
'''

sftp = ssh.open_sftp()
with sftp.open('C:/apps/bot-keo-nhom-bcr-main/vps_diag3.py', 'w') as f:
    f.write(remote.encode('utf-8'))
sftp.close()
stdin, stdout, stderr = ssh.exec_command(r'C:\tools\python\python.exe C:\apps\bot-keo-nhom-bcr-main\vps_diag3.py')
print(stdout.read().decode('utf-8', errors='replace'))
ssh.close()
