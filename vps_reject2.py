import paramiko, sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('180.93.235.84', 22, 'administrator', 'uK?fdJ4Qo!7v', timeout=20)
remote = r'''
import re
for i in [1,3]:
    p = rf"C:\apps\bot-keo-nhom-bcr-main\logs\session{i}-out.log"
    with open(p, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()[-15000:]
    for kw in ["LOBBY", "FATAL UI", "SCREENSHOT FAIL", "chụp ảnh thành công", "REJECT", "SIGNAL LOST", "FATAL SESSION", "notify-screenshot"]:
        c = sum(1 for l in lines if kw.lower() in l.lower())
        if c:
            print(f"NS{i} {kw}: {c}")
    print(f"NS{i} --- last matches ---")
    pat = re.compile(r"LOBBY|SCREENSHOT FAIL|chụp ảnh thành công|FATAL SESSION|REJECT|SIGNAL LOST", re.I)
    for l in lines:
        if pat.search(l):
            last = l.rstrip()
    try:
        print(last.encode("ascii","backslashreplace").decode())
    except: pass
'''
sftp = ssh.open_sftp()
with sftp.open('C:/apps/bot-keo-nhom-bcr-main/t3.py', 'w') as f:
    f.write(remote.encode('utf-8'))
sftp.close()
stdin, stdout, stderr = ssh.exec_command(r'C:\tools\python\python.exe C:\apps\bot-keo-nhom-bcr-main\t3.py')
print(stdout.read().decode('utf-8', errors='replace'))
ssh.close()
