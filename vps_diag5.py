import paramiko, sys, os, glob
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('180.93.235.84', 22, 'administrator', 'uK?fdJ4Qo!7v', timeout=20)

remote = r'''
import os, re, glob
from urllib.request import urlopen

def safe(s):
    return s.encode("ascii", "backslashreplace").decode("ascii")

try:
    with urlopen("http://127.0.0.1:3201/api/session-progress", timeout=5) as r:
        print("PROGRESS", safe(r.read().decode()))
except Exception as e:
    print("ERR", e)

shots = sorted(glob.glob(r"C:\apps\bot-keo-nhom-bcr-main\public\screenshots\sexy_*.png"), key=os.path.getmtime, reverse=True)[:8]
print("\nLATEST FILES:")
for p in shots:
    st = os.stat(p)
    print(safe(f"{os.path.basename(p)} {st.st_size}B age={__import__('time').time()-st.st_mtime:.0f}s"))

pat = re.compile(r"FATAL|SCREENSHOT|API NOTIFY|CLEAR|OUT BÀN|resetMain|IN ROOM|CHƯA|notify-screenshot|LOBBY|REJECT", re.I)
for i in [1,3]:
    p = rf"C:\apps\bot-keo-nhom-bcr-main\logs\session{i}-out.log"
    with open(p, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()
    hits = [l.rstrip() for l in lines if pat.search(l)]
    print(f"\n=== NS{i} last 25 key lines ===")
    for l in hits[-25:]:
        print(safe(l))
'''

sftp = ssh.open_sftp()
with sftp.open('C:/apps/bot-keo-nhom-bcr-main/vps_diag5.py', 'w') as f:
    f.write(remote.encode('utf-8'))
sftp.close()
stdin, stdout, stderr = ssh.exec_command(r'C:\tools\python\python.exe C:\apps\bot-keo-nhom-bcr-main\vps_diag5.py')
print(stdout.read().decode('utf-8', errors='replace'))
ssh.close()
