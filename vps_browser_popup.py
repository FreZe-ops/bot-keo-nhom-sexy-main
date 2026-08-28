import paramiko, sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('180.93.235.84', 22, 'administrator', 'uK?fdJ4Qo!7v', timeout=25)
remote = r'''
import re
pat = re.compile(r"BROWSER WARN|trình duyệt|Xác nhận|popup|isBrowserSupport|CHROME|Firefox", re.I)
for i in range(1,5):
    p = rf"C:\apps\bot-keo-nhom-bcr-main\logs\session{i}-out.log"
    with open(p,"r",encoding="utf-8",errors="ignore") as f:
        lines = f.readlines()[-8000:]
    hits = [l.rstrip() for l in lines if pat.search(l)]
    print(f"\n=== NS{i} browser/popup ({len(hits)} hits) ===")
    for l in hits[-15:]:
        print(l.encode("ascii","backslashreplace").decode())
'''
sftp = ssh.open_sftp()
with sftp.open('C:/apps/bot-keo-nhom-bcr-main/t_browser.py','w') as f: f.write(remote)
sftp.close()
stdin,stdout,stderr=ssh.exec_command(r'C:\tools\python\python.exe C:\apps\bot-keo-nhom-bcr-main\t_browser.py')
print(stdout.read().decode('utf-8', errors='replace'))
ssh.close()
