import paramiko, sys, re
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('180.93.235.84', 22, 'administrator', 'uK?fdJ4Qo!7v', timeout=20)

remote = r'''
import os, re
def safe(s):
    return s.encode("ascii", "backslashreplace").decode("ascii")
pat = re.compile(r"SCREENSHOT FAIL|SCREENSHOT REJECT|FATAL UI|consecutive=|LOBBY|BLANK|CAPTURE_TIMEOUT|IN ROOM|hết attempt|ENTER RETRY|CHƯA VÀO", re.I)
base = r"C:\apps\bot-keo-nhom-bcr-main"
for i in range(1, 5):
    p = os.path.join(base, f"logs/session{i}-out.log")
    with open(p, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()
    hits = [l.rstrip() for l in lines if pat.search(l)]
    print("\n=== NS%d screenshot/enter failures (last 20) ===" % i)
    for l in hits[-20:]:
        print(safe(l))
'''

sftp = ssh.open_sftp()
with sftp.open('C:/apps/bot-keo-nhom-bcr-main/vps_diag4.py', 'w') as f:
    f.write(remote.encode('utf-8'))
sftp.close()
stdin, stdout, stderr = ssh.exec_command(r'C:\tools\python\python.exe C:\apps\bot-keo-nhom-bcr-main\vps_diag4.py')
print(stdout.read().decode('utf-8', errors='replace'))
ssh.close()
