import paramiko
import time
import sys
import os

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HOST = "180.93.235.84"
USER = "administrator"
PASS = "uK?fdJ4Qo!7v"
BASE = r"C:\apps\bot-keo-nhom-bcr-main"
NSSM = r"C:\tools\nssm\nssm-2.24\win64\nssm.exe"
ROOT = os.path.dirname(os.path.abspath(__file__))

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, 22, USER, PASS, timeout=25)
sftp = ssh.open_sftp()
sftp.put(os.path.join(ROOT, "session_watchdog_5m.py"), f"{BASE}/session_watchdog_5m.py")
sftp.close()

for svc in ["BCR-bot2", "BCR-session2", "BCR-watchdog"]:
    ssh.exec_command(f'"{NSSM}" restart {svc}')
    print(f"restart {svc}")
    time.sleep(3)

_, o, _ = ssh.exec_command(f'"{NSSM}" status BCR-bot2')
print("BCR-bot2:", o.read().decode("utf-8", "replace").strip())
_, o, _ = ssh.exec_command(f'"{NSSM}" status BCR-session2')
print("BCR-session2:", o.read().decode("utf-8", "replace").strip())
ssh.close()
print("done")
