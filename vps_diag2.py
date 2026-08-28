import paramiko, json, sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('180.93.235.84', 22, 'administrator', 'uK?fdJ4Qo!7v', timeout=20)

remote = r'''
import os, re, subprocess, json
from urllib.request import urlopen

base = r"C:\apps\bot-keo-nhom-bcr-main"
keys = re.compile(
    r"ENTER|IN ROOM|CLICK TABLE|API NOTIFY|ENTER RETRY|BROWSER|probe|resetMain|"
    r"SHUTDOWN|AUTO ENTER|HALL|WATCHDOG|reserved|popup|maintenance|ALREADY IN",
    re.I,
)

def safe(s):
    return s.encode("ascii", "backslashreplace").decode("ascii")

for ep in ["/api/active-tables", "/api/session-progress"]:
    try:
        with urlopen("http://127.0.0.1:3201" + ep, timeout=5) as r:
            print("=== API", ep, "===")
            print(safe(r.read().decode("utf-8", errors="replace")))
    except Exception as e:
        print("=== API", ep, "ERR", e)

for i in range(1, 5):
    path = os.path.join(base, f"logs/session{i}-out.log")
    prog = os.path.join(base, f"logs_progress_ns{i}")
    print("\n" + "=" * 20 + f" NS{i} " + "=" * 20)
    for p in [path, prog]:
        if not os.path.exists(p):
            print("MISSING", p)
            continue
        with open(p, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
        hits = [l.rstrip() for l in lines if keys.search(l)]
        print(f"--- {os.path.basename(p)} total={len(lines)} hits={len(hits)} ---")
        for line in hits[-35:]:
            print(safe(line))
        if not hits:
            print("last 8 lines:")
            for line in lines[-8:]:
                print(safe(line.rstrip()))
'''

sftp = ssh.open_sftp()
with sftp.open('C:/apps/bot-keo-nhom-bcr-main/vps_diag2.py', 'w') as f:
    f.write(remote.encode('utf-8'))
sftp.close()

stdin, stdout, stderr = ssh.exec_command(r'C:\tools\python\python.exe C:\apps\bot-keo-nhom-bcr-main\vps_diag2.py')
print(stdout.read().decode('utf-8', errors='replace'))
err = stderr.read().decode('utf-8', errors='replace')
if err.strip():
    print('STDERR', err)
ssh.close()
