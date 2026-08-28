"""Quick VPS enter/capture status after deploy."""
import paramiko
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HOST = "180.93.235.84"
USER = "administrator"
PASS = "uK?fdJ4Qo!7v"

REMOTE = r'''
import re, glob, os, time, json
from urllib.request import urlopen

for ns in ["NS1","NS2","NS3","NS4"]:
    try:
        with urlopen(f"http://127.0.0.1:3201/api/get-active-table?nameService={ns}", timeout=4) as r:
            d = json.loads(r.read().decode())
        print(f"{ns} active={d.get('activeTable')} ready={d.get('ready')}")
    except Exception as e:
        print(f"{ns} err={e}")

shots = sorted(glob.glob(r"C:\apps\bot-keo-nhom-bcr-main\public\screenshots\sexy_*.png"), key=os.path.getmtime, reverse=True)[:4]
now = time.time()
for p in shots:
    sz = os.path.getsize(p) // 1024
    print(f"SHOT {os.path.basename(p)} age={int(now-os.path.getmtime(p))}s size={sz}KB")

keys = re.compile(r"IN ROOM|gettext|probe|còn sảnh|LOBBY DETECTED|CAP OK|click.*thất bại|popup|zone_bet|iframeGameTable", re.I)
for i in range(1, 5):
    p = rf"C:\apps\bot-keo-nhom-bcr-main\logs\session{i}-out.log"
    with open(p, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()[-120:]
    print(f"\n--- NS{i} tail ---")
    for l in lines:
        if keys.search(l):
            print(l.rstrip()[:200].encode("ascii", "backslashreplace").decode())
'''

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, 22, USER, PASS, timeout=25)
sftp = ssh.open_sftp()
with sftp.open("C:/apps/bot-keo-nhom-bcr-main/vps_enter_status.py", "w") as f:
    f.write(REMOTE)
sftp.close()
stdin, stdout, stderr = ssh.exec_command(
    r"C:\tools\python\python.exe C:\apps\bot-keo-nhom-bcr-main\vps_enter_status.py"
)
print(stdout.read().decode("utf-8", errors="replace"))
err = stderr.read().decode("utf-8", errors="replace")
if err.strip():
    print("STDERR:", err)
ssh.close()
