import paramiko, sys, glob, os, time
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('180.93.235.84', 22, 'administrator', 'uK?fdJ4Qo!7v', timeout=20)
remote = r'''
import os, re, glob, time
from urllib.request import urlopen

def safe(s):
    return s.encode("ascii", "backslashreplace").decode("ascii")

try:
    with urlopen("http://127.0.0.1:3201/api/session-progress", timeout=5) as r:
        print("PROGRESS", safe(r.read().decode()))
except Exception as e:
    print("ERR", e)

now = time.time()
shots = sorted(glob.glob(r"C:\apps\bot-keo-nhom-bcr-main\public\screenshots\sexy_*.png"), key=os.path.getmtime, reverse=True)[:12]
print("\nRECENT SCREENSHOTS:")
for p in shots:
    st = os.stat(p)
    print(safe(f"  {os.path.basename(p)} | {st.st_size//1024}KB | {now-st.st_mtime:.0f}s ago"))

pat = re.compile(r"FATAL UI|resetMain|SCREENSHOT SAVED|chụp ảnh thành công|API NOTIFY|IN ROOM|ANH|CHƯA VÀO|CLEAR\]", re.I)
base = r"C:\apps\bot-keo-nhom-bcr-main"
for i in range(1, 5):
    p = os.path.join(base, f"logs/session{i}-out.log")
    if not os.path.exists(p):
        continue
    with open(p, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()
    hits = [l.rstrip() for l in lines if pat.search(l)]
    fatal = sum(1 for l in lines[-5000:] if "FATAL UI" in l and "resetMain" in l)
    saved = sum(1 for l in lines[-3000:] if "SCREENSHOT SAVED" in l)
    print(f"\nNS{i}: log={len(lines)} fatal_reset_last5k={fatal} saves_last3k={saved}")
    for l in hits[-6:]:
        print(" ", safe(l))
'''
sftp = ssh.open_sftp()
with sftp.open('C:/apps/bot-keo-nhom-bcr-main/quick_status.py', 'w') as f:
    f.write(remote.encode('utf-8'))
sftp.close()
stdin, stdout, stderr = ssh.exec_command(r'C:\tools\python\python.exe C:\apps\bot-keo-nhom-bcr-main\quick_status.py')
print(stdout.read().decode('utf-8', errors='replace'))
ssh.close()
